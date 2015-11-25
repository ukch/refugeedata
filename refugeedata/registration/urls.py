from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^ajax_image_upload/$', views.image_upload, name='image_upload'),
    url(r'^stage1/$', views.stage_1, name='stage_1'),
    url(r'^stage1/complete/(?P<person_id>\d+)/$',
        views.stage_1_complete, name='stage_1_complete'),
    url(r'^stage2/(?P<person_id>\d+)/$',
        views.stage_2, name='stage_2'),
    url(r'^stage2/complete/(?P<person_id>\d+)/$',
        views.stage_2_complete, name='stage_2_complete'),
]
