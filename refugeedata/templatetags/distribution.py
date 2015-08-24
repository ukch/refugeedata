import django.template

register = django.template.Library()

from refugeedata import models


@register.filter
def has_recipients_for(distribution, template):
    assert isinstance(distribution, models.Distribution)
    return len(template.get_invitees(distribution)) >= 1
