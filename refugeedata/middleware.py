from django.apps import apps
from django.http import HttpResponseRedirect

from django.contrib.sites.models import Site
from django.contrib.sites.requests import RequestSite


def get_current_site(request):
    """
    Version of sites.shortcuts.get_current_site that always uses the request
    """
    # Imports are inside the function because its point is to avoid importing
    # the Site models when django.contrib.sites isn't installed.
    if apps.is_installed('django.contrib.sites'):
        return Site.objects._get_site_by_request(request)
    else:
        return RequestSite(request)


class EnforceCurrentSiteMiddleware():
    """Make sure the current site is one of those listed in Sites.
    If it is not, redirect to the correct site."""

    def process_request(self, request):
        try:
            request.site = get_current_site(request)
        except Site.DoesNotExist:
            request.site = None
            a_site = Site.objects.all()[0]
            absolute_uri = "//{}{}".format(a_site.domain, request.path)
            return HttpResponseRedirect(absolute_uri)
