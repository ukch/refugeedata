from django.conf import settings
from django.core.management.base import CommandError, NoArgsCommand

from django.contrib.sites.models import Site


class Command(NoArgsCommand):

    help = ("Updates the default Site based on the DEFAULT_DOMAIN environment "
            "variable.")

    def handle_noargs(self, **options):
        if not settings.DEFAULT_DOMAIN:
            raise CommandError(
                "The DEFAULT_DOMAIN environment variable is not configured.")
        site = Site.objects.all()[0]
        site.domain = settings.DEFAULT_DOMAIN
        site.save()
        if options.get("verbosity"):
            self.stdout.write("Default Site updated to use domain={}".format(
                site.domain))
