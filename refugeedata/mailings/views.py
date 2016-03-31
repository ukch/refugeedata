import functools

from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.contrib.auth.decorators import user_passes_test

from .. import models, utils
from ..decorators import cache_control
from . import forms

require_staff = user_passes_test(lambda u: u.is_staff)


def _send_email(data):
    send_mail(data["subject"], data["body"],
              settings.DEFAULT_FROM_EMAIL, data["to"],
              fail_silently=False)


def _send_sms(data):
    # FIXME this is slow. Farm it out to a worker.
    utils.send_sms(to=data["to"], body=data["body"])


@require_staff
@cache_control(24 * 60 * 60)
def home(request, type_=models.ONE_DIGIT_CODE_EMAIL,
         template_name="mailings/home.html"):
    ctx = {}
    if type_ == models.ONE_DIGIT_CODE_EMAIL:
        is_sms = False
        form_type = forms.SendEmailForm
        from_address = settings.DEFAULT_FROM_EMAIL
        send_msg = _send_email
    else:
        is_sms = True
        form_type = forms.SendSMSForm
        from_address = getattr(settings, "TWILIO_FROMSMS", None)
        ctx["has_twilio"] = hasattr(settings, "TWILIO_SID")
        send_msg = _send_sms
    if request.method == "POST":
        form = form_type(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            send_msg(data)
            url = reverse("mailings:success")
            if "next" in request.GET:
                url += "?next=" + request.GET["next"]
            return HttpResponseRedirect(url)
    else:
        form = form_type(request.GET if "body" in request.GET else None)
    ctx.update({
        "is_sms": is_sms,
        "from_address": from_address,
        "form": form,
    })
    return render(request, template_name, ctx)

send_sms = functools.partial(home, type_=models.ONE_DIGIT_CODE_SMS)


@require_staff
@cache_control(24 * 60 * 60)
def success(request, template_name="mailings/success.html"):
    if "next" in request.GET:
        next_url = request.GET["next"]
    else:
        next_url = reverse("mailings:home")
    return render(request, template_name, {
        "next_url": next_url,
    })
