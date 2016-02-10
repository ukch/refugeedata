import django.forms as forms

from django.utils.translation import ugettext_lazy as _


class MailingForm(forms.Form):

    to = forms.CharField(required=True, label=_("To"))
    subject = forms.CharField(required=True, label=_("Subject"))
    body = forms.CharField(
        required=True, widget=forms.Textarea, label=_("Message Body"))

    def clean_to(self):
        to = self.cleaned_data["to"]
        to_list = []
        for item in to.split(";"):
            item = item.strip()
            if item == "":
                continue
            # Really basic email validation
            if "@" not in item:
                raise forms.ValidationError(
                    _("'{item}' does not look like an email address.").format(
                        item=item))
            to_list.append(item)
        return to_list
