from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="public.html"),
        name='public'),
    url(r'^registration/', include('refugeedata.registration.urls',
        app_name="registration", namespace="reg")),

    url(r'^admin/', include(admin.site.urls)),
]
