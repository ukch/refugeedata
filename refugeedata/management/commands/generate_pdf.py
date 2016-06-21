import os
import tempfile
import time

import pyratemp
import six
from z3c.rml import rml2pdf

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from refugeedata.exceptions import SitesNotInstalledError
from refugeedata.models import RegistrationCardBatch
from refugeedata.utils import DjangoFormatParser


class Command(BaseCommand):

    help = "Generate a PDF for the specified RegistrationCardBatch"

    TEMPLATE_FILENAME = "assets/cards.rml.tmpl"

    def add_arguments(self, parser):
        parser.add_argument("batch_ids", type=int, nargs="+",
                            help="IDs to generate PDFs for")

    def parse_template(self, template, cards):
        try:
            return str(template(
                cards=cards,
                phone=getattr(settings, "CONTACT_PHONE_NUMBER", ""),
                email=getattr(settings, "CONTACT_EMAIL_ADDRESS", ""),
            ))
        except SitesNotInstalledError:
            raise CommandError("Unknown domain. Please set the DEFAULT_DOMAIN "
                               "environment variable, then run ./manage.py "
                               "update_site")

    def create_pdf_from_batch(self, batch):
        template = pyratemp.Template(filename=self.TEMPLATE_FILENAME,
                                     parser_class=DjangoFormatParser)
        cards = batch.registration_numbers.all()
        rml = six.BytesIO(self.parse_template(template, cards))
        unused, filename = tempfile.mkstemp()
        try:
            rml2pdf.go(rml, filename)  # This closes the file
            new_filename = "{}.pdf".format(time.strftime("%m%d%H%M%S"))
            with open(filename) as fh:
                batch.data_file.save(name=new_filename, content=File(fh))
        finally:
            os.unlink(filename)

    def handle(self, batch_ids, **options):
        batches = RegistrationCardBatch.objects.filter(id__in=batch_ids)
        if batches.count() < len(batch_ids):
            raise CommandError("Batches with IDs {} not found".format(list(
                set(batch_ids).difference(batches.values_list("id", flat=True))
            )))
        for batch in batches:
            self.create_pdf_from_batch(batch)
