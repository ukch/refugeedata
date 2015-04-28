from django.db import models

from django.utils.translation import gettext_lazy as _

from uuidfield import UUIDField

from . import utils


class RegistrationNumber(models.Model):
    """ A registration number, linked to a QR code, that is printed on a card.
    It is not necessarily assigned to a person.
    """

    id = UUIDField(auto=True, primary_key=True)
    number = models.PositiveSmallIntegerField()
    active = models.BooleanField(default=False)

    def __unicode__(self):
        return u"{}: {}".format(self.number, self.id)


class RegistrationCardBatch(models.Model):
    """ A batch of registration numbers, linked to the generation of a PDF.
    This can be auto-generated alongside registration numbers, or linked to
    existing registration numbers.
    """
    registration_numbers = models.ManyToManyField(RegistrationNumber)
    pdf = models.FileField(blank=True, null=True)

    @property
    def registration_number_format(self):
        numbers = self.registration_numbers.order_by("number")
        return utils.format_range(numbers)

    class Meta:
        verbose_name_plural = _("Registration card batches")
