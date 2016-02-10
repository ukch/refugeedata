import django.template
from django.utils.safestring import mark_safe

from refugeedata.distribution.forms import TemplateVariableForm
from refugeedata.utils import (
    TemplateWithDefaultFallback,
    get_keys_from_session,
)

register = django.template.Library()


class HighlightedTemplate(TemplateWithDefaultFallback):

    replace_variable_with = mark_safe(u'<span class="variable">{}</span>')

    def __init__(self, *args, **kwargs):
        super(HighlightedTemplate, self).__init__(*args, **kwargs)
        self._tmpl_context = {}

    def add_tmpl_context(self, **kwargs):
        self._tmpl_context.update(kwargs)

    def __unicode__(self):
        return self.render(self._tmpl_context)


@register.filter
def highlight_variables(text, distribution):
    dic = distribution.get_template_render_context()
    tmpl = HighlightedTemplate(text)
    tmpl.add_tmpl_context(**dic)
    return tmpl


@register.filter
def add_keys_from_session(tmpl, session):
    assert hasattr(tmpl, "add_tmpl_context"), tmpl  # simple duck-typing
    tmpl.add_tmpl_context(**get_keys_from_session(session))
    return tmpl


@register.filter
def with_locale(tmpl, language_code):
    assert hasattr(tmpl, "add_tmpl_context"), tmpl  # simple duck-typing
    tmpl.add_tmpl_context(locale=language_code)
    return tmpl


# FIXME should this tag be inside distribution?
@register.inclusion_tag("inc/template_variable_update.html",
                        takes_context=True)
def variable_name_to_form(context, variable):
    request = context["request"]
    field_value = request.session.get(
        "template_variable_{}_value".format(variable))
    form = TemplateVariableForm(variable, initial={"variable": field_value})
    return {
        "distribution_id": context["distribution"].id,
        "variable": variable,
        "request": request,
        "form": form,
    }
