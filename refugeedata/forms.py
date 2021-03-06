import django.forms as forms

from django.contrib.admin.widgets import AdminIntegerFieldWidget

from django.utils.translation import ugettext_lazy as _

import pyratemp

from . import models, utils


class BatchAdminForm(forms.ModelForm):

    registration_numbers = forms.IntegerField(
        label=_("Number of cards to add"),
        widget=AdminIntegerFieldWidget,
    )

    class Meta:
        model = models.RegistrationCardBatch
        fields = [
            "registration_numbers",
        ]

    def clean_registration_numbers(self):
        number_to_create = self.cleaned_data["registration_numbers"]
        try:
            starting_number = (
                models.RegistrationNumber.objects.order_by("-number")[0].number)
        except IndexError:
            starting_number = 0
        regs = [models.RegistrationNumber(number=obj_number+starting_number)
                for obj_number in xrange(1, number_to_create + 1)]
        return regs


class DistributionAdminForm(forms.ModelForm):

    class Meta:
        model = models.Distribution
        exclude = ["invitees", "attendees", "finish_number"]


class PersonAdminForm(forms.ModelForm):

    class Meta:
        model = models.Person
        exclude = ["registration_card"]


class TemplateAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TemplateAdminForm, self).__init__(*args, **kwargs)
        field = self.fields.get("text")
        if field is not None:
            field.help_text = "<br>\n".join([
                'Basic templating is allowed, using <a '
                'href="{url}">Django-like syntax</a>.'.format(
                    # TODO write my own basic documentation
                    url=("https://docs.djangoproject.com/en/1.8/ref/templates/"
                         "language/")),
                "The following template variables are provided: distribution; "
                "distribution_numbers; distribution_times",
            ])

    def clean_text(self):
        text = self.cleaned_data["text"]
        try:
            utils.TemplateWithDefaultFallback(text).render({})
        except pyratemp.TemplateSyntaxError as e:
            raise forms.ValidationError(e)
        return text
