from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'refugeedata.distribution.views.home', name='home'),
    url(r'^(?P<distribution_id>\d+)/$', 'refugeedata.distribution.views.info', name='info'),
]
