

import datetime

from django.core.management.base import BaseCommand

from refugeedata.models import Distribution, Person


class Command(BaseCommand):

    help = ("Update attendance statistics for yesterday's distribution, or "
            "for all time if 'force' is specified.")

    def add_arguments(self, parser):
        parser.add_argument("-f", "--force", action="store_true",
                            help="Forcibly update all attendance stats")

    def handle(self, force=False, verbosity=1, **options):
        if force:
            people = Person.objects.exclude(
                registration_card__distributions_invited_to=None)
        else:
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            try:
                dist = Distribution.objects.get(date=yesterday)
            except Distribution.DoesNotExist:
                self.stdout.write(
                    "No distribution found for {}. Exiting.".format(yesterday))
                return
            people = dist.invitees.all()
        if verbosity > 1:
            self.stdout.write("Updating {} people...".format(people.count()))
        for person in people:
            person.attendance_percent = (
                person.registration_card.distributions_attended.count() /
                person.registration_card.distributions_invited_to.count()
            ) * 100
            person.save()
        if verbosity > 1:
            self.stdout.write("Done.")
