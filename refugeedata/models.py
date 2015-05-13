from django.conf import settings
from django.db import models

from django.utils.translation import ugettext_lazy as _

from django_languages import LanguageField
from uuidfield import UUIDField

from . import utils


class RegistrationNumber(models.Model):
    """ A registration number, linked to a QR code, that is printed on a card.
    It is not necessarily assigned to a person.
    """

    id = UUIDField(auto=True, primary_key=True, verbose_name=_("ID"))
    number = models.PositiveSmallIntegerField(verbose_name=_("number"))
    active = models.BooleanField(default=False, verbose_name=_("active"))

    class Meta:
        verbose_name = _("Registration Number")
        verbose_name_plural = _("Registration Numbers")
        ordering = ("number", )

    def short_id(self):
        """The first few digits of the ID.
        This is shortened so as to make QR codes easier to scan and IDs easier
        to manually input."""
        return str(self.id)[0:settings.ID_LENGTH]
    short_id.short_description = _("ID")

    def __unicode__(self):
        return u"{}: {}".format(self.number, self.short_id())


class RegistrationCardBatch(models.Model):
    """ A batch of registration numbers, linked to the generation of a PDF.
    This can be auto-generated alongside registration numbers, or linked to
    existing registration numbers.
    """
    registration_numbers = models.ManyToManyField(
        RegistrationNumber,
        verbose_name=_("Registration Numbers"))
    data_file = models.FileField(blank=True, null=True,
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


class Person(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    preferred_lang = models.ForeignKey(Language,
                                       verbose_name=_("Preferred language"))
    needs = models.TextField(blank=True, null=True, verbose_name=_("Needs"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email"))
    # TODO incredibly basic phone number validation
    phone = models.CharField(max_length=20, blank=True, null=True,
                             verbose_name=_("Phone Number"))
    preferred_contact = models.CharField(max_length=1, choices=[
        ("P", _("Phone")),
        ("E", _("Email")),
    ], default="E", verbose_name=_("Preferred Contact"))
    story = models.TextField(blank=True, null=True, verbose_name=_("Story"))
    active = models.BooleanField(default=True, verbose_name=_("Active"))

    # Populated by mobile (although fallback is available)
    registration_card = models.OneToOneField(
        RegistrationNumber,
        related_name="person",
        limit_choices_to={"person": None, "active": False},
        verbose_name=_("Registration Card"),
    )
    photo = models.ImageField(blank=True, null=True, verbose_name=_("Photo"))

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("People")
