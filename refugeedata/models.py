from django.db import models

from uuidfield import UUIDField


class RegistrationNumber(models.Model):
    """ A registration number, linked to a QR code, that is printed on a card.
    It is not necessarily assigned to a person.
    """

    id = UUIDField(auto=True, primary_key=True)
    number = models.PositiveSmallIntegerField()
    active = models.BooleanField(default=False)
