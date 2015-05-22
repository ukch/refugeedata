from django.conf.urls import url
import django.contrib.auth.views as auth_views

from refugeedata import views


urlpatterns = [
    url(r'check_login/$', views.check_login, name="check_login"),
    url(r'^login/$', views.login, name="login"),
    url(r'^logout/$', views.logout, name="logout"),
]
