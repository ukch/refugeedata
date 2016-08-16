from __future__ import division

import datetime
from functools import partial
import operator
import os

from django.core.urlresolvers import resolve, Resolver404
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
import django.template.loader as loader
from django.shortcuts import redirect, render
from django.views.generic import RedirectView

import django.contrib.auth.views as auth_views

from .decorators import cache_control
from .models import Distribution, Person

SOURCE_URL = "https://github.com/ukch/refugeedata"


# TODO is this safe? Will it respect logins?
@cache_control(1 * 60 * 60)
def home(request):
    if request.user.has_perm("refugeedata.add_person"):
        return redirect("reg:home")
    return render(request, "public.html", {
        "site_name": request.site.name,
        "source_url": SOURCE_URL,
        "next_distribution": Distribution.objects.upcoming().first(),
    })


def scan_card(request, card_number, card_code):
    try:
        dist = Distribution.objects.get(date=datetime.date.today())
    except Distribution.DoesNotExist:
        dist = None
    if dist:
        return redirect("dist:attendee", dist.id, card_number, card_code)
    return redirect("public")


class MyRedirectView(RedirectView):

    extra_kwargs = None

    def get_redirect_url(self, *args, **kwargs):
        if self.extra_kwargs is not None:
            kwargs.update(self.extra_kwargs)
        return super(MyRedirectView, self).get_redirect_url(*args, **kwargs)

redirect_to_scan_card = MyRedirectView.as_view(
    permanent=True,
    pattern_name="scan_card",
    extra_kwargs={"card_code": "0000"},
)


def check_login(request):
    if request.user.is_authenticated():
        url = request.GET.get("next", settings.LOGIN_REDIRECT_URL)
        return HttpResponseRedirect(url)
    else:
        url = settings.LOGIN_URL
        return HttpResponseRedirect(
            "{}?{}".format(url, request.GET.urlencode()))


def _find_app_from_path(path):
    path_with_slash = path if path.endswith("/") else "{}/".format(path)
    try:
        match = resolve(path_with_slash)
    except Resolver404:
        path, remainder = os.path.split(path)
        if not remainder:
            return
        return _find_app_from_path(path)
    if match.app_name is None:
        path, remainder = os.path.split(path)
        if not remainder:
            return
        return _find_app_from_path(path)
    return match.app_name


def login(request, template_name="login.html"):
    base_template = "base.html"
    if "next" in request.GET:
        app = _find_app_from_path(request.GET["next"])
        base_template = loader.select_template(
            [os.path.join(app, "base.html"), base_template])
    else:
        app = None
    return auth_views.login(
        request, template_name=template_name, current_app=app, extra_context={
            "base_template": base_template,
        })


logout = partial(auth_views.logout, next_page="/")


@user_passes_test(lambda u: u.is_superuser, login_url="admin:login")
def show_faces(request, template_name="admin/show_faces.html"):
    people = Person.objects.filter(active=True).exclude(photo="")\
        .select_related("registration_card")
    return render(request, template_name, {
        "title": _("Faces"),
        "site_url": "/",
        "people": people,
    })


@user_passes_test(lambda u: u.is_superuser, login_url="admin:login")
def attendance(request, template_name="admin/attendance.html"):
    people = Person.objects.filter(active=True)\
        .select_related("registration_card")
    people_list = []
    for person in people:
        person_list = {
            "obj": person,
            "invited":
                person.registration_card.distributions_invited_to.count(),
            "attended":
                person.registration_card.distributions_attended.count(),
        }
        if person_list["invited"]:
            person_list["attendance"] = (
                person_list["attended"] / person_list["invited"] * 100)
        else:
            # Person has never been invited to a distribution
            continue
        people_list.append(person_list)
    return render(request, template_name, {
        "title": _("Distribution attendance"),
        "site_url": "/",
        "people": sorted(people_list,
                         key=operator.itemgetter("attendance"))[:100]
    })


# Error handlers
def error_page(request, template_name, code):
    base_template = "base.html"
    current_app = _find_app_from_path(request.path)
    if current_app:
        base_template = loader.select_template(
            [os.path.join(current_app, "base.html"), "base.html"])
    return render(request, template_name, {
        "base_template": base_template,
        "bugs_url": "{}/issues/".format(SOURCE_URL)
    }, current_app=current_app, status=code)


page_not_found = partial(error_page, template_name="404.html", code=404)
server_error = partial(error_page, template_name="500.html", code=500)
permission_denied = partial(error_page, template_name="403.html", code=403)
