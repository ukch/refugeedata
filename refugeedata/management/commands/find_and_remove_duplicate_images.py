from django.core.management.base import NoArgsCommand
from django.db.models import Count

from refugeedata.models import Person


class Command(NoArgsCommand):

    help = ("Find all people who have the same name as each other, and remove "
            "all but the latter")

    def handle_noargs(self, verbosity=1, **options):
        # Find the duplicate image names
        # see http://stackoverflow.com/questions/8989221/
        duplicate_photo_names = (Person.objects.exclude(photo='')
            .values("photo")
            .annotate(Count('id')).order_by()
            .filter(id__count__gt=1)
            .values_list("photo", flat=True))
        total_count = 0
        for filename in duplicate_photo_names:
            if verbosity > 1:
                self.stdout.write(filename)
            people = Person.objects.filter(photo=filename).order_by("-id")
            total_count += (people.count() - 1)
            people.exclude(id=people.last().id).update(photo="")
        self.stdout.write("{} record(s) updated".format(total_count))
