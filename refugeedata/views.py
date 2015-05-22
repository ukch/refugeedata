import datetime
from functools import partial
import os

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

import django.contrib.auth.views as auth_views

from .models import Distribution


def home(request):
    if request.user.is_superuser:
        return redirect("admin:index")
    if request.user.has_perm("refugeedata.add_person"):
        return redirect("reg:home")
    return render(request, "public.html")


def scan_card(request, card_number, card_code):
    try:
        dist = Distribution.objects.get(date=datetime.date.today())
    except Distribution.DoesNotExist:
        dist = None
    if dist and request.user.has_perm("registration", obj=dist):
        return redirect("dist:attendee", dist.id, card_number, card_code)
    return redirect("public")


def check_login(request):
    if request.user.is_authenticated():
        url = request.GET.get("next", settings.LOGIN_REDIRECT_URL)
        return HttpResponseRedirect(url)
    else:
        url = settings.LOGIN_URL
        return HttpResponseRedirect(
            "{}?{}".format(url, request.GET.urlencode()))


def login(request, template_name="login.html"):
    app = request.GET.get("app", "public")
    base_template = os.path.join(app, "base.html")
    return auth_views.login(
        request, template_name=template_name, current_app=app, extra_context={
            "base_template": base_template,
        })


logout = partial(auth_views.logout, next_page="/")
