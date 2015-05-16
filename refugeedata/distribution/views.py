import datetime

from django.shortcuts import get_object_or_404, redirect, render

from refugeedata import models

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
    people = models.Person.objects.filter(id__in=person_ids).exclude(
        **{preferred_contact: ""})
    recipients = people.values_list(preferred_contact, flat=True)
    return render(request, "distribution/template_mock_send.html", {
        "distribution": distribution,
        "template": template,
        "recipients": recipients
    })
