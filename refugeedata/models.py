from django.conf import settings
from django.db import models
from django.dispatch import receiver

from django.utils import formats
from django.utils.translation import ugettext_lazy as _

from django_languages import LanguageField
from uuidfield import UUIDField

from . import utils


SMS_OR_EMAIL = [
    ("P", _("SMS")),
    ("E", _("Email")),
]


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
        max_length=1, choices=SMS_OR_EMAIL, default="E",
        verbose_name=_("Preferred Contact"))
    story = models.TextField(blank=True, null=True, verbose_name=_("Story"))
    active = models.BooleanField(default=True, verbose_name=_("Active"))

    # Populated by mobile (although fallback is available)
    registration_card = models.OneToOneField(
        RegistrationNumber,
        related_name="person",
        limit_choices_to={"person": None, "active": False},
        verbose_name=_("Registration Card"),
    )
    photo = models.ImageField(blank=True, null=True, upload_to="user_images",
                              verbose_name=_("Photo"))

    def __unicode__(self):
        return u"{}: {}".format(self.registration_card.number, self.name)

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("People")
        ordering = ("registration_card__number", )


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


class Distribution(models.Model):
    """A distribution day.
    This model holds data about distribution date and expected/actual
    attendees.
    """
    date = models.DateField(verbose_name=_("Distribution Date"))
    supplies_quantity = models.SmallIntegerField(
        verbose_name=_("Supplies Quantity"))
    supplies_description = models.TextField(
        blank=True, null=True, verbose_name=_("Supplies Description"))
    invitees = models.ManyToManyField(RegistrationNumber,
                                      related_name="distributions_invited_to")
    attendees = models.ManyToManyField(
        RegistrationNumber, related_name="distributions_attended", blank=True)
    templates = models.ManyToManyField(Template, verbose_name=_("Templates"))
    finish_number = models.PositiveSmallIntegerField(blank=True, null=True)

    def __unicode__(self):
        return unicode(formats.date_format(self.date))

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
