from itertools import groupby
from functools import cmp_to_key
from operator import itemgetter
import time
import hashlib
import uuid

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver

from django.utils import formats
from django.utils.translation import ugettext_lazy as _

from django_languages import LanguageField
from six.moves import map
from imagekit.models import ProcessedImageField
from uuidfield import UUIDField

from . import exceptions, managers, utils
from .processors import RotateAndScale


ONE_DIGIT_CODE_SMS = "P"
ONE_DIGIT_CODE_EMAIL = "E"
SMS_OR_EMAIL = [
    (ONE_DIGIT_CODE_SMS, _("SMS")),
    (ONE_DIGIT_CODE_EMAIL, _("Email")),
]


def manual_uuid_generation():
    return uuid.uuid4().get_hex()


class RegistrationNumber(models.Model):
    """ A registration number, linked to a QR code, that is printed on a card.
    It is not necessarily assigned to a person.
    """

    id = UUIDField(auto=True, primary_key=True, verbose_name=_("ID"),
                   default=manual_uuid_generation)
    number = models.PositiveSmallIntegerField(verbose_name=_("number"))
    active = models.BooleanField(default=False, verbose_name=_("active"))
    short_id_missing = models.BooleanField(default=False, verbose_name=_("short ID missing"))

    class Meta:
        verbose_name = _("Registration Number")
        verbose_name_plural = _("Registration Numbers")
        ordering = ("number", )

    def short_id(self):
        """The first few digits of the ID.
        This is shortened so as to make QR codes easier to scan and IDs easier
        to manually input."""
        if self.short_id_missing:
            return "0" * settings.ID_LENGTH
        return str(self.id)[0:settings.ID_LENGTH]
    short_id.short_description = _("ID")

    def get_absolute_url(self):
        return reverse("scan_card", args=[self.number, self.short_id()])

    @property
    def qr_code_url(self):
        relative_url = self.get_absolute_url()
        try:
            site = get_current_site(None)
        except AttributeError:
            raise exceptions.SitesNotInstalledError()
        else:
            absolute_url = "http://{}/{}".format(site.domain, relative_url)
        return utils.qr_code_from_url(absolute_url, size=130)

    def __unicode__(self):
        return unicode(self.number)


class RegistrationCardBatch(models.Model):
    """ A batch of registration numbers, linked to the generation of a PDF.
    This can be auto-generated alongside registration numbers, or linked to
    existing registration numbers.
    """
    registration_numbers = models.ManyToManyField(
        RegistrationNumber,
        verbose_name=_("Registration Numbers"))
    data_file = models.FileField(blank=True, null=True, upload_to="card_data",
                                 verbose_name=_("Data File"))

    def __unicode__(self):
        return unicode(self.registration_number_format())

    def registration_number_format(self):
        numbers = self.registration_numbers.order_by("number")
        return utils.format_range(numbers)
    registration_number_format.short_description = _("Number Range")

    class Meta:
        ordering = ("id", )
        verbose_name = _("Registration Card Batch")
        verbose_name_plural = _("Registration Card Batches")


class Language(models.Model):
    iso_code = LanguageField(verbose_name=_("Base Language"))
    description = models.CharField(max_length=255,
                                   verbose_name=_("Description"))
    example_text = models.TextField(max_length=255,
                                    verbose_name=_("Example Text"))

    def __unicode__(self):
        return u"{}: {}".format(self.iso_code, self.description)

    class Meta:
        ordering = ("iso_code", )
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")


USER_IMAGE_PREFIX = "user_images/%m%d%H%M%S/"


class Person(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    preferred_lang = models.ForeignKey(Language,
                                       verbose_name=_("Preferred language"))
    needs = models.TextField(blank=True, null=True, verbose_name=_("Needs"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email"))
    # TODO incredibly basic phone number validation
    phone = models.CharField(max_length=20, blank=True, null=True,
                             verbose_name=_("Phone Number"))
    preferred_contact = models.CharField(
        max_length=1, choices=SMS_OR_EMAIL, default=ONE_DIGIT_CODE_SMS,
        verbose_name=_("Preferred Contact"))
    story = models.TextField(blank=True, null=True, verbose_name=_("Story"))
    number_of_dependents = models.PositiveSmallIntegerField(
        default=0, verbose_name=_("Number of Dependents"))
    active = models.BooleanField(default=True, verbose_name=_("Active"))

    # Populated by mobile (although fallback is available)
    registration_card = models.OneToOneField(
        RegistrationNumber,
        related_name="person",
        limit_choices_to={"person": None, "active": False},
        verbose_name=_("Registration Card"),
    )
    photo = ProcessedImageField(
        blank=True, null=True, upload_to=USER_IMAGE_PREFIX,
        verbose_name=_("Photo"),
        processors=[RotateAndScale(max_width=600, max_height=800)])

    def get_absolute_url(self):
        return reverse("reg:stage_2_complete", args=[self.id])

    def __unicode__(self):
        return u"{}: {}".format(self.registration_card.number, self.name)

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("People")
        ordering = ("registration_card__number", )


class DistributionTime(models.Model):
    """The time of the distribution."""

    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ("start_time", )

    def __unicode__(self):
        return u"{} - {}".format(self.start_time, self.end_time)


class MissingContext(Exception):

    pass


class Template(models.Model):
    """An Email or SMS template to be sent to attendees."""

    type = models.CharField(max_length=1, choices=SMS_OR_EMAIL,
                            verbose_name=_("Template Type"))
    language = models.ForeignKey(Language, verbose_name=_("Language"))
    text = models.TextField(verbose_name=_("Template Text"))

    def __unicode__(self):
        return u"{}: {}".format(self.get_type_display(), self.text)

    class Meta:
        verbose_name = _("Template")
        verbose_name_plural = _("Templates")

    def get_invitees(self, distribution=None):
        if distribution:
            cards = distribution.invitees.all()
        else:
            cards = RegistrationNumber.objects.filter(active=True)
        person_ids = \
            cards.exclude(person=None).values_list("person", flat=True)
        preferred_contact = ("phone" if self.type == ONE_DIGIT_CODE_SMS
                             else "email")
        people = Person.objects.filter(
            id__in=person_ids, preferred_lang=self.language).exclude(**{
                preferred_contact: "",
            })
        return people.values_list(preferred_contact, flat=True)

    def get_rendered_text(self, context):
        """Render the text using pyratemp."""
        missing = set()
        for required in utils.get_variable_names_from_template(self):
            if required not in context:
                missing.add(required)
        if missing:
            raise MissingContext(missing)
        tmpl = utils.PyratempTemplate(self.text)
        context = context.copy()
        context["locale"] = self.language.iso_code
        return tmpl.render(context)


def _sort_by_previous_finish(finish):
    def _sort(x, y):
        if x[0] > finish and y[0] <= finish:
            # x < y
            return -1
        elif y[0] > finish and x[0] <= finish:
            # x > y
            return 1
        # x == y
        return 0

    return _sort


class Distribution(models.Model):
    """A distribution day.
    This model holds data about distribution date and expected/actual
    attendees.
    """
    date = models.DateField(verbose_name=_("Distribution Date"), unique=True)
    supplies_quantity = models.SmallIntegerField(
        verbose_name=_("Supplies Quantity"))
    supplies_description = models.TextField(
        blank=True, null=True, verbose_name=_("Supplies Description"))
    times = models.ManyToManyField(
        DistributionTime, verbose_name=_("Distribution Times"), blank=True)
    invitees = models.ManyToManyField(RegistrationNumber,
                                      related_name="distributions_invited_to")
    attendees = models.ManyToManyField(
        RegistrationNumber, related_name="distributions_attended", blank=True)
    templates = models.ManyToManyField(Template, verbose_name=_("Templates"))
    finish_number = models.PositiveSmallIntegerField(blank=True, null=True)

    objects = managers.DistributionManager()

    @property
    def hash(self):
        timestamp = time.mktime(self.date.timetuple())
        secret = "".join(c.encode("hex") for c in settings.SECRET_KEY)
        secret_int = int(secret[:8], 16)
        return hashlib.sha1(str(timestamp + secret_int)).hexdigest()[:4]

    def check_hash(self, password):
        return password == self.hash

    def __unicode__(self):
        return unicode(formats.date_format(self.date))

    @property
    def numbers(self):
        if not hasattr(self, "_numbers"):
            numbers = self.invitees.values_list("number", flat=True)
            # Taken from http://stackoverflow.com/questions/2154249/
            max_padding = 5
            groups = []
            for key, group in groupby(enumerate(numbers),
                                      lambda (index, item): index - item):
                group = list(map(itemgetter(1), group))
                if len(groups) and groups[-1][1] + max_padding >= group[0]:
                    # There is a small gap between the groups. If the cards in
                    # this gap are all deactivated, pretend it's not there.
                    extras = range(groups[-1][1] + 1, group[0])
                    inactive_extras = RegistrationNumber.objects.filter(
                        active=False, number__in=extras)
                    if inactive_extras.count() == len(extras):
                        group[0], unused = groups.pop()
                groups.append((group[0], group[-1]))
            try:
                previous = Distribution.objects.get(id=self.id - 1)
            except Distribution.DoesNotExist:
                pass
            else:
                groups.sort(key=cmp_to_key(
                    _sort_by_previous_finish(previous.finish_number)))
            self._numbers = groups
        return self._numbers

    def show_numbers(self):
        return "; ".join((u"#{}".format(begin) if begin == end else
                          u"#{} \u2013 #{}".format(begin, end)
                          for begin, end in self.numbers))

    def get_absolute_url(self):
        return reverse("dist:info", args=[self.id])

    def get_template_render_context(self):
        """Return the 'free' context used to render email/SMS templates."""
        return {
            "distribution": self,
            "distribution_numbers": self.numbers,
            "distribution_times": self.times.all(),
        }

    class Meta:
        verbose_name = _("Distribution")
        verbose_name_plural = _("Distributions")
        ordering = ("date", )


@receiver(models.signals.post_save, sender=Distribution)
def set_invitees_and_finish_number(instance, created, **kwargs):
    if created:
        dists = Distribution.objects.exclude(id=instance.id).order_by("id")
        last_created_dist = dists.reverse().first()
        if last_created_dist:
            starting_number = last_created_dist.finish_number + 1
        else:
            starting_number = 1
        active_cards = RegistrationNumber.objects.filter(active=True)
        cards = active_cards.filter(number__gte=starting_number)
        cards = list(cards[:instance.supplies_quantity])
        difference = instance.supplies_quantity - len(cards)
        if difference:
            cards += list(active_cards[:difference])
        instance.invitees = cards
        instance.finish_number = cards[-1].number
        instance.save()
