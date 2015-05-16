import datetime

from django.shortcuts import redirect, render

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
