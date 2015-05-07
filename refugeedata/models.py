from django.db import models

from django.utils.translation import ugettext_lazy as _

from django_languages import LanguageField
from uuidfield import UUIDField

from . import utils


class RegistrationNumber(models.Model):
    """ A registration number, linked to a QR code, that is printed on a card.
    It is not necessarily assigned to a person.
    """

    id = UUIDField(auto=True, primary_key=True)
    number = models.PositiveSmallIntegerField()
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ("number", )

    def __unicode__(self):
        return u"{}: {}".format(self.number, self.id)


class RegistrationCardBatch(models.Model):
    """ A batch of registration numbers, linked to the generation of a PDF.
    This can be auto-generated alongside registration numbers, or linked to
    existing registration numbers.
    """
    registration_numbers = models.ManyToManyField(RegistrationNumber)
    pdf = models.FileField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.registration_number_format)

    @property
    def registration_number_format(self):
        numbers = self.registration_numbers.order_by("number")
        return utils.format_range(numbers)

    class Meta:
        ordering = ("id", )
        verbose_name_plural = _("Registration card batches")


class Language(models.Model):
    iso_code = LanguageField(verbose_name=_("Base Language"))
    description = models.CharField(max_length=255)
    example_text = models.TextField(max_length=255)

    def __unicode__(self):
        return u"{}: {}".format(self.iso_code, self.description)


class Person(models.Model):
    name = models.CharField(max_length=255)
    preferred_lang = models.ForeignKey(Language,
                                       verbose_name=_("Preferred language"))
    needs = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    # TODO incredibly basic phone number validation
    phone = models.CharField(max_length=20, blank=True, null=True)
    preferred_contact = models.CharField(max_length=1, choices=[
        ("P", _("Phone")),
        ("E", _("Email")),
    ], default="E")
    story = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    # Populated by mobile (although fallback is available)
    registration_card = models.OneToOneField(RegistrationNumber, blank=True,
                                             null=True)
    photo = models.ImageField(blank=True, null=True)
