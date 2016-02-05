import datetime

from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render, Http404

from django.contrib.admin.views.decorators import staff_member_required

from refugeedata import models

from refugeedata.utils import get_variable_names_from_template
from . import forms
from .decorators import standard_distribution_access, handle_template_errors


def home(request):
    try:
        dist = models.Distribution.objects.get(date=datetime.date.today())
    except models.Distribution.DoesNotExist:
        if request.user.is_superuser:
            raise Http404("No distribution today")
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
        models.RegistrationNumber, active=True, number=card_number)
    if card.short_id() != card_code:
        raise Http404("Invalid card code")
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


@staff_member_required
@handle_template_errors
def templates(request, distribution):
    template_variables = set()
    for template in distribution.templates.all():
        template_variables = template_variables\
                .union(get_variable_names_from_template(template))\
                .difference({"distribution", "start_num", "end_num"})
    return render(request, "distribution/templates.html", {
        "distribution": distribution,
        "template_variables": template_variables,
        "email_templates": distribution.templates.filter(
            type=models.ONE_DIGIT_CODE_EMAIL),
        "sms_templates": distribution.templates.filter(
            type=models.ONE_DIGIT_CODE_SMS),
    })


@staff_member_required
@handle_template_errors
def template_variable_set(request, distribution, variable):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    form = forms.TemplateVariableForm(variable, request.POST)
    if form.is_valid():
        key = "template_variable_{}_value".format(variable)
        request.session[key] = form.cleaned_data["variable"]
        request.session.save()
    return redirect(request.GET.get("next", "/"))


@staff_member_required
@handle_template_errors
def template_mock_send(request, distribution, template_id):
    template = get_object_or_404(models.Template, id=template_id)
    args = []
    if "to_everyone" not in request.GET:
        args.append(distribution)
    recipients = template.get_invitees(*args)
    if len(recipients) == 0:
        raise Http404("No recipients found")
    return render(request, "distribution/template_mock_send.html", {
        "distribution": distribution,
        "template": template,
        "recipients": recipients
    })
