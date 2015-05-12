from django.conf import settings
from django.http import HttpResponseRedirect

from django.contrib.sites.middleware import CurrentSiteMiddleware
from django.contrib.sites.models import Site


class EnforceCurrentSiteMiddleware(CurrentSiteMiddleware):
    """Make sure the current site is one of those listed in Sites.
    If it is not, redirect to the correct site."""

    def process_request(self, request):
        try:
            super(EnforceCurrentSiteMiddleware, self).process_request(request)
        except Site.DoesNotExist:
            request.site = None
            a_site = Site.objects.all()[0]
            absolute_uri = "//{}{}".format(a_site.domain, request.path)
            return HttpResponseRedirect(absolute_uri)
