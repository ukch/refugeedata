from django.db.models.manager import Manager
from django.utils.timezone import now


class DistributionManager(Manager):

    def upcoming(self):
        return self.get_queryset().filter(date__gt=now())

    def past(self):
        return self.get_queryset().filter(date__lt=now()).order_by("-date")
