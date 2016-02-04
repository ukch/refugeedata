import django.template
from django.utils.safestring import mark_safe

from refugeedata.distribution.forms import TemplateVariableForm
from refugeedata.utils import TemplateWithDefaultFallback

register = django.template.Library()


class HighlightedTemplate(TemplateWithDefaultFallback):

    replace_variable_with = mark_safe('<span class="variable">{}</span>')


@register.filter
def highlight_variables(text, session):
    dic = {}
    for key, value in session.iteritems():
        if key.startswith("template_variable_"):
            dic[key[18:][:-6]] = value
    return HighlightedTemplate(text).render(dic)


# FIXME should this tag be inside distribution?
@register.inclusion_tag("inc/template_variable_update.html",
                        takes_context=True)
def variable_name_to_form(context, variable):
    request = context["request"]
    field_value = request.session.get(
        "template_variable_{}_value".format(variable))
    form = TemplateVariableForm(variable, initial={"variable": field_value})
    return {
        "distribution_id": context["distribution"].id,
        "variable": variable,
        "request": request,
        "form": form,
    }
