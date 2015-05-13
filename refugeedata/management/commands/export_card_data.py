import csv
import os
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from refugeedata.models import RegistrationCardBatch


class Command(BaseCommand):

    help = ("Exports the data from a card batch as CSV, and optionally saves "
            "to the model.")

    def add_arguments(self, parser):
        parser.add_argument("batch_id", type=int)
        parser.add_argument("--save", action="store_true", default=False,
                            help="Save to the model instead of outputting to "
                                 "stdout")

    def generate_csv(self, cards, out):
        """Generate a CSV representation of the given cards' data"""
        writer = csv.writer(out)

        # Header row
        writer.writerow(["Number", "Short ID", "Active"])
        for card in cards:
            writer.writerow([card.number, card.short_id(), card.active])

    def handle(self, batch_id, save=False, **options):
        try:
            batch = RegistrationCardBatch.objects.get(id=batch_id)
        except RegistrationCardBatch.DoesNotExist, e:
            raise CommandError(e)
        cards = batch.registration_numbers.all()
        if save:
            with NamedTemporaryFile(prefix="export-", suffix=".csv") as fh:
                self.generate_csv(cards, out=fh)
                batch.data_file.save(name=fh.name, content=File(fh))
            if options["verbosity"]:
                self.stdout.write("File {} created.".format(
                    os.path.join(settings.MEDIA_ROOT, batch.data_file.name)))
        else:
            self.generate_csv(cards, out=self.stdout)
