import functools
from itertools import chain
import re
import urllib

from django.conf import settings
from django.template import defaultfilters
from django.utils.safestring import SafeData
from django.utils.translation import ugettext as _

from babel.dates import format_date, format_time
from memoize import memoize
import phonenumbers
import pytz
import pyratemp
import six
from twilio.rest import TwilioRestClient


class InvalidNumber(Exception):
    pass


def get_keys_from_session(session):
    dic = {}
    for key, value in session.iteritems():
        if key.startswith("template_variable_"):
            dic[key[18:][:-6]] = value
    return dic


def takes_locale(func, kwarg_name):
    """Specifies that a filter function can be locale-specific"""
    @functools.wraps(func)
    def wrapper(locale, *args, **kwargs):
        kwargs[kwarg_name] = locale
        return func(*args, **kwargs)
    wrapper.takes_locale = True
    return wrapper


def my_format_time(*args, **kwargs):
    kwargs.setdefault("format", "short")
    return format_time(*args, **kwargs)


FILTER_REGISTRY = {
    "date": defaultfilters.date,
    "localdate": takes_locale(format_date, "locale"),
    "timeformat": takes_locale(my_format_time, "locale"),
}


class PyratempRegexFixMeta(type):

    """Pyratemp doesn't build its regexes properly. Fix that."""

    def __new__(cls, name, bases, dic):
        klass = type(name, bases, dic)
        # build regexps
        # comment
        #   single-line, until end-tag or end-of-line.
        klass._strComment = r"%s(?P<content>.*?)(?P<end>%s|\n|$)" % (
            re.escape(klass._comment_start), re.escape(klass._comment_end))
        klass._reComment = re.compile(klass._strComment, re.M)

        # escaped or unescaped substitution
        #   single-line ("|$" is needed to be able to generate good error-messges)
        klass._strSubstitution = r"""
            (
            %s\s*(?P<sub>.*?)\s*(?P<end>%s|$)       #substitution
            |
            %s\s*(?P<escsub>.*?)\s*(?P<escend>%s|$) #escaped substitution
            )
        """ % (re.escape(klass._sub_start), re.escape(klass._sub_end),
               re.escape(klass._subesc_start), re.escape(klass._subesc_end))
        klass._reSubstitution = re.compile(klass._strSubstitution, re.X | re.M)

        # block
        #   - single-line, no nesting.
        #   or
        #   - multi-line, nested by whitespace indentation:
        #       * start- and end-tag of a block must have exactly the same indentation.
        #       * start- and end-tags of *nested* blocks should have a greater indentation.
        # NOTE: A single-line block must not start at beginning of the line with
        #       the same indentation as the enclosing multi-line blocks!
        #       Note that "       " and "\t" are different, although they may
        #       look the same in an editor!
        _s = klass._block_start
        _e = klass._block_end
        klass._strBlock = r"""
                    ^(?P<mEnd>[ \t]*)%send%s(?P<meIgnored>.*)\r?\n?   # multi-line end  (^   <!--(end)-->IGNORED_TEXT\n)
                    |
                    (?P<sEnd>)%send%s                               # single-line end (<!--(end)-->)
                    |
                    (?P<sSpace>[ \t]*)                              # single-line tag (no nesting)
                    %s(?P<sKeyw>\w+)[ \t]*(?P<sParam>.*?)%s
                    (?P<sContent>.*?)
                    (?=(?:%s.*?%s.*?)??%send%s)                     # (match until end or i.e. <!--(elif/else...)-->)
                    |
                                                                    # multi-line tag, nested by whitespace indentation
                    ^(?P<indent>[ \t]*)                             #   save indentation of start tag
                    %s(?P<mKeyw>\w+)\s*(?P<mParam>.*?)%s(?P<mIgnored>.*)\r?\n
                    (?P<mContent>(?:.*\n)*?)
                    (?=(?P=indent)%s(?:.|\s)*?%s)                   #   match indentation
                """ % (_s, _e,
                       _s, _e,
                       _s, _e, _s, _e, _s, _e,
                       _s, _e, _s, _e)
        klass._reBlock = re.compile(klass._strBlock, re.X | re.M)
        return klass


@six.add_metaclass(PyratempRegexFixMeta)
class DjangoFormatParser(pyratemp.Parser):

    # template-syntax
    _comment_start = "{#"
    _comment_end = "#}"
    _subesc_start = "{{"
    _subesc_end = "}}"
    _block_start = "{%\s?"
    _block_end = "\s?%}"

    end_synonyms = frozenset(["endif", "endfor"])

    def __init__(self, filename=None, *args, **kwargs):
        self.filename = filename
        super(DjangoFormatParser, self).__init__(*args, **kwargs)

    def _parse(self, template, fpos=0):
        if self._includestack[-1][0] == None:
            self._includestack[-1] = (self.filename, self._includestack[-1][1])
        for end_synonym in self.end_synonyms:
            template = template.replace(end_synonym, "end")
        return super(DjangoFormatParser, self)._parse(template, fpos=fpos)


@six.add_metaclass(PyratempRegexFixMeta)
class DjangoFormatParserWithCustomTagHandler(DjangoFormatParser):

    def __init__(self, *args, **kwargs):
        # Keep track of the for-loops that we are replacing
        self.forloop_fallbacks = set()
        self.forloop_defined_variables = {}
        super(DjangoFormatParserWithCustomTagHandler, self).__init__(
            *args, **kwargs)

    def parse(self, template, replace_variable_with):
        """Do our own parsing on 'for' nodes, so they appear usefully."""
        superclass = super(DjangoFormatParserWithCustomTagHandler, self)
        parsetree = []
        for elem in superclass.parse(template):
            if elem[0] == "for":
                names, iterable = elem[1:3]
                parsetree.append(("str", u"%s for %s in %s %s\n" % (
                    "{%",
                    u", ".join(replace_variable_with.format(name)
                               for name in names),
                    replace_variable_with.format(iterable),
                    "%}",
                )))
                self.forloop_fallbacks.add(iterable)
                self.forloop_defined_variables[iterable] = names
                parsetree += elem[3]
                parsetree.append(("str", "{% endfor %}\n"))
            else:
                parsetree.append(elem)
        return parsetree


def test_expression(expr):
    if expr == "i==1":
        # The test expr: pass without questioning
        return
    if "|" in expr:
        expr, fltr = expr.split("|", 1)
        fltr = fltr.split(":", 1)[0]
        if fltr not in FILTER_REGISTRY:
            raise SyntaxError(_("Filter '{name}' is not defined. Please "
                                "choose from one of {filters}.").format(
                    name=fltr, filters=FILTER_REGISTRY.keys()))
    if not re.match(r"^[a-zA-Z_.]+$", expr):
        raise SyntaxError(_("Expression must be made up of upper or lowercase "
                          "letters and underscores."))


class PyratempTemplate(pyratemp.Renderer):

    """Wrapper around pyratemp.Template to use the Django template API"""

    PARSER_CLASS = DjangoFormatParser

    def __init__(self, template_string, filename=None):
        self.filename = filename
        self.parsetree = self.parser.parse(template_string)
        self.escapefunc = pyratemp.escape

    @property
    def parser(self):
        if not hasattr(self, "_parser"):
            self._parser = self.PARSER_CLASS(
                self.filename, testexpr=test_expression)
        return self._parser

    def _parse_expr(self, expr):
        if "|" not in expr:
            return expr, None, None
        expr, fltr = expr.split("|", 1)
        if ":" not in fltr:
            return expr, fltr, []
        fltr, arg = fltr.split(":", 1)
        return expr, fltr, [arg]

    def _handle_filter(self, var, fltr, args, locale=None):
        args = [a.strip("'").strip('"') for a in args]
        func = FILTER_REGISTRY[fltr]
        if hasattr(func, "takes_locale"):
            if locale is None:
                raise SyntaxError(
                    _("'{name}' filter requires locale").format(name=fltr))
            func = functools.partial(func, locale)
        return func(var, *args)

    def evalfunc(self, expr, variables):
        expr, fltr, args = self._parse_expr(expr)
        var_name, remainder = (expr + ".").split(".", 1)
        var = variables[var_name]
        for part in remainder.split("."):
            if part == "":
                continue
            try:
                var = getattr(var, part)
            except AttributeError:
                raise KeyError(part)
        if fltr:
            return self._handle_filter(
                var, fltr, args, variables.get("locale"))
        return var

    def render(self, context, *extra):
        superclass = super(PyratempTemplate, self)
        if len(extra):
            # context is a parsetree, extra is [context]
            return superclass.render(context, *extra)
        assert isinstance(context, dict), context
        tokens = superclass.render(self.parsetree, context)
        return pyratemp._dontescape("".join(tokens))


class TemplateWithDefaultFallback(PyratempTemplate):
    """Don't leave unresolved context variables empty; leave them as-is."""

    replace_variable_with = u"{}"

    PARSER_CLASS = DjangoFormatParserWithCustomTagHandler

    @property
    def parser(self):
        if not hasattr(self, "_parser"):
            self._parser = super(TemplateWithDefaultFallback, self).parser
            self._parser.parse = functools.partial(
                self._parser.parse,
                replace_variable_with=self.replace_variable_with,
            )
        return self._parser

    def evalfunc(self, expr, variables):
        try:
            value = super(TemplateWithDefaultFallback, self).evalfunc(
                expr, variables)
        except KeyError:
            value = "{{ %s }}" % expr
        safe = isinstance(
            self.replace_variable_with, (pyratemp._dontescape, SafeData))
        value = self.replace_variable_with.format(value)
        if safe:
            value = pyratemp._dontescape(value)
        return value


class NameHarvesterTemplate(TemplateWithDefaultFallback):

    def __init__(self, *args, **kwargs):
        self.harvested_variable_names = None
        self.forloop_defined_variables = None
        super(NameHarvesterTemplate, self).__init__(*args, **kwargs)

    def _parse_expr(self, expr):
        expr, fltr, args = super(NameHarvesterTemplate, self)._parse_expr(expr)
        if self.harvested_variable_names is not None:
            name = expr.split(".", 1)[0]
            if name not in self.forloop_defined_variables:
                self.harvested_variable_names.add(name)
        return expr, fltr, args

    def render(self, context, *extra):
        self.harvested_variable_names = {
            self._parse_expr(expr)[0]
            for expr in self.parser.forloop_fallbacks
        }
        self.forloop_defined_variables = {
            name
            for names in self.parser.forloop_defined_variables.itervalues()
            for name in names
        }
        return super(NameHarvesterTemplate, self).render(context, *extra)

    def harvest_names(self):
        self.render({})
        return self.harvested_variable_names


def get_variable_names_from_template(template):
    template = NameHarvesterTemplate(template.text, template.id)
    return template.harvest_names()


def format_range(values):
    """Attempts to present the given range in a human-readable format

    >>> format_range([1])
    '1'
    >>> format_range([1,2,3])
    '1:3'
    >>> format_range([1,2,3,5,6])
    '1:3,5:6'
    >>> format_range([1,2,3,5,6,8,10])
    '1:3,5:6,8,10'
    """

    if hasattr(values, "values_list"):
        # We need iter here because values_list returns a special QuerySet
        # object, not a list.
        return format_range(iter(values.values_list("number", flat=True)))

    values = iter(values)
    beginning = end = None

    def _iter(values):
        # We use _iter here to mutate values
        prev = values.next()
        while True:
            try:
                current = values.next()
            except StopIteration, e:
                yield prev, None
                raise e
            yield prev, current
            prev = current

    for prev, current in _iter(values):
        if not beginning:
            beginning = end = prev
        if current:
            if prev == current - 1:
                end = current
            else:
                break
    if beginning is not None:
        if beginning == end:
            this_range = str(beginning)
        else:
            this_range = "{}:{}".format(beginning, end)
        extra = format_range(chain([current], values))
        if extra:
            return "{},{}".format(this_range, extra)
        else:
            return this_range


QR_CODE_URL_TEMPLATE = ("https://chart.googleapis.com/chart?cht=qr"
                        "&chs={size}x{size}&chl={data}&chId=L|2")


def qr_code_from_url(relative_url, request=None, size=500):
    if request:
        url = request.build_absolute_uri(relative_url)
    else:
        url = relative_url
    return QR_CODE_URL_TEMPLATE.format(size=size, data=urllib.quote_plus(url))


def send_sms(to, body):
    """Sends an SMS using the Twilio API library
    arguments:
    to: a list of phone numbers (may or may not be valid)
    body: a string containing the body of the message to be sent
    """
    account_sid = settings.TWILIO_SID
    auth_token = settings.TWILIO_AUTHTOKEN
    fromsms = settings.TWILIO_FROMSMS
    client = TwilioRestClient(account_sid, auth_token)
    for number in to:
        client.messages.create(to=number, from_=fromsms, body=body)


@memoize(timeout=300)
def timezone_to_country_code(tz_name):
    mapping = {tz: country
               for country, tz_list in pytz.country_timezones.iteritems()
               for tz in tz_list}
    return mapping[tz_name]


def to_international_format(local_number):
    country_code = timezone_to_country_code(settings.TIME_ZONE)
    number = phonenumbers.parse(local_number, region=country_code)
    if not phonenumbers.is_valid_number(number):
        raise InvalidNumber(number)
    return phonenumbers.format_number(
        number, phonenumbers.PhoneNumberFormat.E164)
