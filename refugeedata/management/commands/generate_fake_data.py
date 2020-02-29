from datetime import datetime, timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

try:
    from pip_local import import_module
except ImportError:
    from importlib import import_module

from refugeedata.models import RegistrationNumber, Language

from model_mommy import mommy


class Command(BaseCommand):

    help = ("Generates fake data and inserts it into the database. CAUTION "
            "do not use this with a production database!")

    def handle(self, **kwargs):
        try:
            names = import_module("names")
        except SystemExit as e:
            raise CommandError("Pip install failed.")

        languages = Language.objects.all()
        if languages.count() == 0:
            raise CommandError(
                "It looks like the initial data has not been loaded. Please "
                "run `manage.py loaddata initial_data`."
            )
        elif languages.count() > 1:
            # Basic sanity-checking
            raise CommandError(
                "I don't think this database is clean so I'm refusing to do "
                "anything."
            )

        # Create users
        mommy.make("refugeedata.Person", preferred_lang=languages.first(),
                   name=names.get_full_name, _quantity=50)

        # Activate all registration cards
        RegistrationNumber.objects.update(active=True)

        # Create distributions: 9 in the past, 1 today
        now = datetime.now()

        # Past dates
        for i in xrange(10):
            date = (now - timedelta(weeks=i)).date()
            mommy.make("refugeedata.Distribution", date=date,
                       supplies_quantity=25)

        call_command("update_attendance", "-f")
