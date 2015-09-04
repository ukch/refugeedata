from django.conf import settings
from django.conf.urls import include, url, static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.views.generic import RedirectView

handler404 = "refugeedata.views.page_not_found"
handler500 = "refugeedata.views.server_error"
handler403 = "refugeedata.views.permission_denied"

urlpatterns = [
    url(r'^$', 'refugeedata.views.home', name='public'),
    url(r'^c/(?P<card_number>\d+)/(?P<card_code>[a-fA-F0-9]{4})/$',
        'refugeedata.views.scan_card', name="scan_card"),
    url(r'^accounts/', include('refugeedata.app.auth_urls',
        app_name="distribution", namespace="auth")),
    url(r'^grappelli/', include('grappelli.urls')),
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
