import datetime
import functools

from pyratemp import TemplateSyntaxError, TemplateRenderError

from django.contrib.auth import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from refugeedata.models import Distribution, Template

from .forms import DistributionHashForm


def standard_distribution_access(func):
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        dist = get_object_or_404(
            Distribution, id=kwargs.pop('distribution_id'))
        if not request.user.is_superuser:
            if dist.date != datetime.date.today():
                raise PermissionDenied()
            if not request.user.has_perm("distribution", obj=dist):
                if request.method == "POST":
                    form = DistributionHashForm(dist, request.POST)
                    if form.is_valid():
                        request.session["distribution_hash"] = \
                            form.cleaned_data["password"]
                        return redirect(request.path)
                else:
                    form = DistributionHashForm(dist)
                return render(request, "distribution/login.html", {
                    "distribution": dist,
                    "form": form,
                })

        kwargs['distribution'] = dist
        return func(request, *args, **kwargs)

    return wrapper


def handle_template_errors(func):
    @functools.wraps(func)
    def wrapper(request, distribution_id, *args, **kwargs):
        distribution = get_object_or_404(Distribution, id=distribution_id)
        try:
            return func(request, distribution, *args, **kwargs)
        except (TemplateSyntaxError, TemplateRenderError) as e:
            if hasattr(e, "filename"):
                template_id = e.filename
            else:
                template_id = kwargs.get("template_id")
            if template_id:
                template = Template.objects.filter(id=template_id).first()
            return render(request, "distribution/template_syntax_error.html", {
                "distribution": distribution,
                "template": template,
                "exception": e,
            }, status=400)

    return wrapper
