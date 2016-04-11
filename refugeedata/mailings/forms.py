from collections import OrderedDict

import django.forms as forms

from django.utils.translation import ugettext_lazy as _

from .. import utils


class MailerFormBase(forms.Form):
    to = forms.CharField(required=True, label=_("To"))
    body = forms.CharField(
        required=True, widget=forms.Textarea, label=_("Message Body"))

    def clean_to(self):
        to = self.cleaned_data["to"]
        to_list = []
        for item in to.split(";"):
            item = item.strip()
            if item == "":
                continue
            to_list.append(self.clean_to_item(item))
        return to_list

    def clean_to_item(self, item):
        raise NotImplementedError(type(self))


class SendEmailForm(MailerFormBase):

    subject = forms.CharField(required=True, label=_("Subject"))

    def __init__(self, *args, **kwargs):
        super(SendEmailForm, self).__init__(*args, **kwargs)
        all_fields = self.fields
        self.fields = OrderedDict()
        for field_name in ["to", "subject", "body"]:
            self.fields[field_name] = all_fields[field_name]

    def clean_to_item(self, item):
        # Really basic email validation
        if "@" not in item:
            raise forms.ValidationError(
                _("'{item}' does not look like an email address.").format(
                    item=item))
        return item


class SendSMSForm(MailerFormBase):

    def clean_to_item(self, item):
        try:
            return utils.to_international_format(item)
        except utils.InvalidNumber:
            raise forms.ValidationError(
                _("{item} is not a valid number.".format(item=item)))
