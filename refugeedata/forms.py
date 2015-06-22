import django.forms as forms

from django.contrib.admin.widgets import AdminIntegerFieldWidget

from django.utils.translation import ugettext_lazy as _

from . import models


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
