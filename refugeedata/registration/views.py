from django.shortcuts import redirect, render, get_object_or_404

from refugeedata import models

from .forms import RegistrationForm


# TODO limit to special users
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            person = form.save()
            return redirect("reg:must_complete", person.id)
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {
        "form": form,
    })


# TODO limit to special users or QR-authorised people
def must_complete(request, person_id):
    person = get_object_or_404(models.Person, id=person_id)
    if person.registration_card and person.photo:
        return redirect("reg:home")
    return render(request, "registration/must_complete.html", {
        "person": person,
    })
