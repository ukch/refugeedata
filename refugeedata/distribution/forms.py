import django.forms as forms

from django.utils.translation import ugettext_lazy as _

import refugeedata.models as models


class DistributionHashForm(forms.Form):

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "size": 4,
        "maxlength": 4,
    }))

    def __init__(self, dist, *args, **kwargs):
        self.dist = dist
        super(DistributionHashForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data["password"]
        if self.dist.check_hash(password):
            return password
        else:
            raise forms.ValidationError(_("Incorrect password"))


class DistributionNumberForm(forms.Form):

    number = forms.IntegerField(label=_("Number"))

    def __init__(self, distribution, *args, **kwargs):
        super(DistributionNumberForm, self).__init__(*args, **kwargs)
        self.distribution = distribution

    def clean_number(self):
        number = self.cleaned_data["number"]
        invitees = self.distribution.invitees.all()
        if number not in invitees.values_list("number", flat=True):
            raise forms.ValidationError(
                _("{} is not part of this distribution.".format(number)))
        return number


class DistributionAddPhotoForm(forms.ModelForm):

    photo = forms.ImageField(label=_("Add a photo"), required=True)

    class Meta:
        model = models.Person
        fields = ["photo"]


class TemplateVariableForm(forms.Form):

    variable = forms.CharField(required=False)

    def __init__(self, variable_name, *args, **kwargs):
        super(TemplateVariableForm, self).__init__(*args, **kwargs)
        field = self.fields["variable"]
        field.label = variable_name
        field.widget.attrs["id"] = "id_variable_{}".format(variable_name)
