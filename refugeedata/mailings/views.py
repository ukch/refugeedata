from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.contrib.auth.decorators import user_passes_test

from . import forms

require_staff = user_passes_test(lambda u: u.is_staff)


@require_staff
def home(request, template_name="mailings/home.html"):
    if request.method == "POST":
        form = forms.MailingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            send_mail(data["subject"], data["body"],
                      settings.DEFAULT_FROM_EMAIL, data["to"],
                      fail_silently=False)
            url = reverse("mailings:success")
            if "next" in request.GET:
                url += "?next=" + request.GET["next"]
            return HttpResponseRedirect(url)
    else:
        form = forms.MailingForm(
            request.GET if "body" in request.GET else None)
    return render(request, template_name, {
        "from_address": settings.DEFAULT_FROM_EMAIL,
        "form": form,
    })


@require_staff
def success(request, template_name="mailings/success.html"):
    if "next" in request.GET:
        next_url = request.GET["next"]
    else:
        next_url = reverse("mailings:home")
    return render(request, template_name, {
        "next_url": next_url,
    })
