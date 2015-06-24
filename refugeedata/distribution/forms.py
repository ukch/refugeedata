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


class DistributionAddPhotoForm(forms.ModelForm):

    photo = forms.ImageField(label=_("Add a photo"), required=True)

    class Meta:
        model = models.Person
        fields = ["photo"]
