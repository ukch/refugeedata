from django.conf import settings
from django.conf.urls import include, url, static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', 'refugeedata.views.home', name='public'),
    url(r'^c/(?P<person_id>\d+)/(?P<person_code>[a-fA-F0-9]{4})/$',
        'refugeedata.views.scan_card', name="scan_card")
]

urlpatterns += i18n_patterns(
    url(r'^$', RedirectView.as_view(pattern_name="public", permanent=True)),
    url(r'^distribution/', include('refugeedata.distribution.urls',
        app_name="distribution", namespace="dist")),
    url(r'^registration/', include('refugeedata.registration.urls',
        app_name="registration", namespace="reg")),
    url(r'^admin/', include(admin.site.urls)),
)
if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
