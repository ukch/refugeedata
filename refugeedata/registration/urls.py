from django.conf.urls import url

from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="registration/index.html"),
        name='home'),
    url(r'^new/$', 'refugeedata.registration.views.register', name='register'),
    url(r'^complete/(?P<person_id>\d+)/$',
        'refugeedata.registration.views.must_complete', name='must_complete'),
]
