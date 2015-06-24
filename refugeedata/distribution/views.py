import datetime

from django.shortcuts import get_object_or_404, redirect, render

from refugeedata import models

from . import forms
from .decorators import standard_distribution_access


def home(request):
    try:
        dist = models.Distribution.objects.get(date=datetime.date.today())
    except models.Distribution.DoesNotExist:
        return redirect("public")
    return redirect("dist:info", dist.id)


@standard_distribution_access
def info(request, distribution):
    return render(request, "distribution/info.html", {
        "distribution": distribution,
    })


@standard_distribution_access
def attendee(request, distribution, card_number, card_code):
    card = get_object_or_404(
        models.RegistrationNumber, active=True, number=card_number,
        id__startswith=card_code)
    if request.method == "POST":
        photo_form = forms.DistributionAddPhotoForm(
            request.POST, request.FILES, instance=card.person)
        if "photo_included" in request.POST:
            if photo_form.is_valid():
                photo_form.save()
        if "photo_included" not in request.POST or photo_form.is_valid():
            distribution.invitees.add(card)
            distribution.attendees.add(card)
            return redirect("dist:info", distribution.id)
    else:
        photo_form = forms.DistributionAddPhotoForm(instance=card.person)
    return render(request, "distribution/attendee.html", {
        "photo_form": photo_form,
        "distribution": distribution,
        "person": card.person,
        "is_invited": card in distribution.invitees.all(),
        "has_attended": card in distribution.attendees.all(),
    })


# FIXME standard dist access or admin-only?
@standard_distribution_access
def templates(request, distribution):
    return render(request, "distribution/templates.html", {
        "distribution": distribution,
        "email_templates": distribution.templates.filter(type="E"),
        "sms_templates": distribution.templates.filter(type="P"),
    })


# FIXME standard dist access or admin-only?
@standard_distribution_access
def template_mock_send(request, distribution, template_id):
    template = get_object_or_404(models.Template, id=template_id)
    if "to_everyone" in request.GET:
        cards = models.RegistrationNumber.objects.filter(active=True)
    else:
        cards = distribution.invitees.all()
    person_ids = cards.exclude(person=None).values_list("person", flat=True)
    preferred_contact = "phone" if template.type == "P" else "email"
    people = models.Person.objects.filter(
        id__in=person_ids, preferred_lang=template.language).exclude(**{
            preferred_contact: "",
        })
    recipients = people.values_list(preferred_contact, flat=True)
    return render(request, "distribution/template_mock_send.html", {
        "distribution": distribution,
        "template": template,
        "recipients": recipients
    })
