from django.shortcuts import redirect, render


def home(request):
    if request.user.is_staff:
        return redirect("admin:index")
    if request.user.has_perm("refugeedata.add_person"):
        return redirect("reg:home")
    return render(request, "public.html")
