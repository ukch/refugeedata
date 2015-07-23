import django.template

from refugeedata.utils import TemplateWithDefaultFallback

register = django.template.Library()


class HighlightedTemplate(TemplateWithDefaultFallback):

    replace_variable_with = '<span class="variable">{}</span>'


@register.filter
def highlight_variables(text):
    empty_context = django.template.Context()
    return HighlightedTemplate(text).render(empty_context)
