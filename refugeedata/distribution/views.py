import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, Http404

from django.contrib.admin.views.decorators import staff_member_required

from six.moves.urllib.parse import urlencode

from refugeedata import models

from refugeedata.utils import (
    get_variable_names_from_template,
    get_keys_from_session,
)
from ..decorators import cache_control
from . import forms
from .decorators import standard_distribution_access, handle_template_errors


# TODO is this safe? Will it respect logins?
@cache_control(1 * 60 * 60)
def home(request):
    try:
        dist = models.Distribution.objects.get(date=datetime.date.today())
    except models.Distribution.DoesNotExist:
        if request.user.is_superuser:
            return render(request, "distribution/upcoming.html", {
                "upcoming": models.Distribution.objects.upcoming(),
                "past": models.Distribution.objects.past(),
            })
        return redirect("public")
    return redirect("dist:info", dist.id)


# TODO is this safe? Will it respect logins?
@cache_control(1 * 60 * 60)
@standard_distribution_access
def info(request, distribution):
    if request.method == "POST":
        form = forms.DistributionNumberForm(distribution, data=request.POST)
        if form.is_valid():
            card = distribution.invitees.get(
                number=form.cleaned_data["number"])
            return redirect("dist:attendee", distribution.id, card.number,
                            card.short_id())
    else:
        form = forms.DistributionNumberForm(distribution)
    return render(request, "distribution/info.html", {
        "distribution": distribution,
        "form": form,
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
            return render(request, "distribution/redirect.html", {
                "redirect_url": reverse("dist:info", args=[distribution.id]),
            })
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
                .difference({"distribution", "distribution_numbers",
                             "distribution_times"})
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
def template_to_mailer(request, distribution, template_id):
    template = get_object_or_404(models.Template, id=template_id)
    args = []
    if "to_everyone" not in request.GET:
        args.append(distribution)
    recipients = template.get_invitees(*args)
    if len(recipients) == 0:
        raise Http404("No recipients found")
    context = get_keys_from_session(request.session)
    context.update(distribution.get_template_render_context())
    try:
        body = template.get_rendered_text(context)
    except models.MissingContext as e:
        variables, = e.args
        return render(request, "distribution/template_missing_context.html", {
            "template_variables": variables,
            "distribution": distribution,
            "template": template,
        })
    params = {
        "body": body.encode("utf-8"),
        "next": request.path,
    }
    if len(recipients) >= 50:
        params["to_template"] = "{}:{}".format(template.id, "" if "to_everyone" in request.GET else distribution.id)
    else:
        params["to"] = "; ".join(recipients)
    url_name = ("mailings:send_email"
                if template.type == models.ONE_DIGIT_CODE_EMAIL
                else "mailings:send_sms")
    url = reverse(url_name) + "?" + urlencode(params)
    return HttpResponseRedirect(url)
