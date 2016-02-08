from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.stage_1, name='home'),
    url(r'^ajax_image_upload/$', views.image_upload, name='image_upload'),
    url(r'^(?P<person_id>\d+)/extra/$',
        views.stage_1_complete, name='stage_1_complete'),
    url(r'^(?P<person_id>\d+)/extra/add$',
        views.stage_2, name='stage_2'),
    url(r'^(?P<person_id>\d+)/$',
        views.stage_2_complete, name='stage_2_complete'),
    url(r'^(?P<person_id>\d+)/edit/$', views.edit, name='edit'),
]
