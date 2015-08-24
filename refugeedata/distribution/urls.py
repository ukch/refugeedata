from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'refugeedata.distribution.views.home', name='home'),
    url(r'^(?P<distribution_id>\d+)/$', 'refugeedata.distribution.views.info', name='info'),
    url(r'^(?P<distribution_id>\d+)/attendee/(?P<card_number>\d+)/(?P<card_code>[a-fA-F0-9]{4})/$',
        'refugeedata.distribution.views.attendee', name='attendee'),
    url(r'^(?P<distribution_id>\d+)/templates/$', 'refugeedata.distribution.views.templates', name='templates'),
    url(r'^(?P<distribution_id>\d+)/templates/set_variable/(?P<variable>[a-zA-Z_]+)/$', 'refugeedata.distribution.views.template_variable_set', name='template_variable_set'),
    url(r'^(?P<distribution_id>\d+)/templates/mock_send/(?P<template_id>\d+)/$',
        'refugeedata.distribution.views.template_mock_send', name='mock_send_email'),
    url(r'^(?P<distribution_id>\d+)/templates/mock_send/(?P<template_id>\d+)/$',
        'refugeedata.distribution.views.template_mock_send', name='mock_send_sms'),
]
