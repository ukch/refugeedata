from django.conf.urls import url

from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="registration/index.html"),
        name='home'),
    url(r'^stage1/$', 'refugeedata.registration.views.stage_1', name='stage_1'),
    url(r'^stage1/complete/(?P<person_id>\d+)/$',
        'refugeedata.registration.views.stage_1_complete', name='stage_1_complete'),
    url(r'^stage2/(?P<person_id>\d+)/$',
        'refugeedata.registration.views.stage_2', name='stage_2'),
    url(r'^stage2/complete/(?P<person_id>\d+)/$',
        'refugeedata.registration.views.stage_2_complete', name='stage_2_complete'),
]
