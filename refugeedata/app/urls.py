from django.conf import settings
from django.conf.urls import include, url, static
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="public.html"),
        name='public'),
    url(r'^registration/', include('refugeedata.registration.urls',
        app_name="registration", namespace="reg")),

    url(r'^admin/', include(admin.site.urls)),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
