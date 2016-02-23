from django.conf import settings
from django.http import HttpResponsePermanentRedirect

from django.contrib.sites.requests import RequestSite


class EnforceSiteURLMiddleware(object):
    """Make sure the current site is one of those listed in Sites.
    If it is not, redirect to the correct site."""

    def process_request(self, request):
        rsite = RequestSite(request)
        # If sites framework is not installed these will always be the same
        if rsite.domain != request.site.domain:
            scheme = "http" if settings.DEBUG else "https"
            absolute_uri = "{}://{}{}".format(
                scheme, request.site.domain, request.path)
            return HttpResponsePermanentRedirect(absolute_uri)


class MaxAgeMiddleware(object):

    def process_response(self, request, response):
        if hasattr(request, "_cache_control_max_age"):
            response['Cache-Control'] = \
                'max-age=%d' % request._cache_control_max_age
        return response
