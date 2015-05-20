import datetime

from django.shortcuts import redirect, render

from .models import Distribution


def home(request):
    if request.user.is_superuser:
        return redirect("admin:index")
    if request.user.has_perm("refugeedata.add_person"):
        return redirect("reg:home")
    return render(request, "public.html")


def scan_card(request, card_number, card_code):
    try:
        dist = Distribution.objects.get(date=datetime.date.today())
    except Distribution.DoesNotExist:
        dist = None
    if dist and request.user.has_perm("registration", obj=dist):
        return redirect("dist:attendee", dist.id, card_number, card_code)
    return redirect("public")
