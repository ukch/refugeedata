import json
import os

from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.generic import RedirectView

from django.utils.http import urlencode
from django.utils import timezone

from refugeedata import models

from .. import utils
from .decorators import (
    register_permission_required, register_or_qr_permission_required)
from .forms import RegistrationForm, RegistrationFormStage2


home = register_permission_required(
    RedirectView.as_view(permanent=False, pattern_name="reg:stage_1"))


@register_permission_required
@require_http_methods(["POST"])
def image_upload(request):
    if "file" not in request.FILES:
        return HttpResponseBadRequest("No file uploaded")
    fh = request.FILES["file"]
    prefix = timezone.now().strftime(models.USER_IMAGE_PREFIX)
    filename = os.path.join(prefix, fh.name)
    default_storage.save(filename, fh)
    return HttpResponse(json.dumps({"filename": filename}),
                        content_type="application/json")


@register_permission_required
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            person = form.save()
            return redirect("reg:stage_1_complete", person.id)
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {
        "form": form,
    })


@register_permission_required
def edit(request, person_id):
    person = get_object_or_404(models.Person, id=person_id)
    if request.method == "POST":
        form = RegistrationForm(request.POST, instance=person)
        if form.is_valid():
            person = form.save()
            if "next" in request.GET:
                return redirect(request.GET["next"])
            return redirect("reg:stage_1_complete", person.id)
    else:
        form = RegistrationForm(instance=person)
    return render(request, "registration/register.html", {
        "form": form,
    })


@register_permission_required
def extra_required(request, person_id):
    person = get_object_or_404(models.Person, id=person_id)
    if person.registration_card and person.photo:
        return redirect("reg:stage_2_complete", person.id)
    url = reverse("reg:stage_2", args=[person.id])
    url_with_login = "{}?{}".format(
        reverse("auth:check_login"), urlencode({"next": url}))
    return render(request, "registration/must_complete.html", {
        "url": url,
        "qr_code": utils.qr_code_from_url(url_with_login, request, size=300),
    })


@register_or_qr_permission_required
def extra(request, person_id):
    person = get_object_or_404(models.Person, id=person_id)
    if person.registration_card and person.photo:
        return redirect("reg:stage_2_complete", person.id)
    if request.method == "POST":
        form = RegistrationFormStage2(request.POST, request.FILES,
                                      instance=person)
        if form.is_valid():
            person = form.save()
            return redirect("reg:stage_2_complete", person.id)
    else:
        form = RegistrationFormStage2(instance=person)
    return render(request, "registration/stage2.html", {
        "form": form,
    })


@register_or_qr_permission_required
def view(request, person_id):
    person = get_object_or_404(models.Person, id=person_id)
    return render(request, "registration/stage2_complete.html", {
        "person": person,
    })


# TODO remove these aliases
stage_1 = register
stage_1_complete = extra_required
stage_2 = extra
stage_2_complete = view
