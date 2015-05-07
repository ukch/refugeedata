from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render, get_object_or_404

from refugeedata import models

from .. import utils
from .forms import RegistrationForm, RegistrationFormStage2


# TODO limit to special users
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


# TODO limit to special users
def stage_1_complete(request, person_id):
    person = get_object_or_404(models.Person, id=person_id)
    if person.registration_card and person.photo:
        return redirect("reg:stage_2_complete", person.id)
    url = reverse("reg:stage_2", args=[person.id])
    return render(request, "registration/must_complete.html", {
        "url": url,
        "qr_code": utils.qr_code_from_url(url, request, size=300),
    })


# TODO limit to special users or QR-authorised people
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


# TODO limit to special users or QR-authorised people
def stage_2_complete(request, person_id):
    person = get_object_or_404(models.Person, id=person_id)
    return render(request, "registration/stage2_complete.html", {
        "person": person,
    })
