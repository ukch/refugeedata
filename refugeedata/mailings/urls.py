from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^email/$', views.send_email, name='send_email'),
    url(r'^sms/$', views.send_sms, name='send_sms'),
    url(r'^success/$', views.success, name='success'),
]
