from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import TemplateView

from django.utils.http import urlencode

from refugeedata import models

from .. import utils
from .decorators import (
    register_permission_required, register_or_qr_permission_required)
from .forms import RegistrationForm, RegistrationFormStage2


home = register_permission_required(
    TemplateView.as_view(template_name="registration/index.html"))


@register_permission_required
def stage_1(request):
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
def stage_1_complete(request, person_id):
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
def stage_2(request, person_id):
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
def stage_2_complete(request, person_id):
    person = get_object_or_404(models.Person, id=person_id)
    return render(request, "registration/stage2_complete.html", {
        "person": person,
    })
