from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'refugeedata.distribution.views.home', name='home'),
    url(r'^(?P<distribution_id>\d+)/$', 'refugeedata.distribution.views.info', name='info'),
    url(r'^(?P<distribution_id>\d+)/attendee/(?P<card_number>\d+)/(?P<card_code>[a-fA-F0-9]{4})/$',
        'refugeedata.distribution.views.attendee', name='attendee'),
    url(r'^(?P<distribution_id>\d+)/templates/$', 'refugeedata.distribution.views.templates', name='templates'),
    url(r'^(?P<distribution_id>\d+)/templates/set_variable/(?P<variable>[a-zA-Z_]+)/$', 'refugeedata.distribution.views.template_variable_set', name='template_variable_set'),
    url(r'^(?P<distribution_id>\d+)/templates/send/(?P<template_id>\d+)/$',
        'refugeedata.distribution.views.template_to_mailer', name='send_email'),
    url(r'^(?P<distribution_id>\d+)/templates/send/(?P<template_id>\d+)/$',
        'refugeedata.distribution.views.template_to_mailer', name='send_sms'),
]
