from collections import OrderedDict

import django.forms as forms

# FIXME forms shouldn't know about HTTP
from django.http import Http404
from django.shortcuts import get_object_or_404

from django.utils.translation import ugettext_lazy as _

from .. import models, utils


class MailerFormBase(forms.Form):
    to = forms.CharField(required=True, label=_("To"))
    body = forms.CharField(
        required=True, widget=forms.Textarea, label=_("Message Body"))
        
    def __init__(self, data=None, *args, **kwargs):
        if data and "to_template" in data:
            data = data.copy()
            template_data = data["to_template"]
            try:
                template_id, distribution_id = template_data.split(":", 1)
                template_id = int(template_id)
                if distribution_id == "":
                    distribution_id = None
                else:
                    distribution_id = int(distribution_id)
            except ValueError:
                raise Http404("Bad to_template value")
            template = get_object_or_404(models.Template, id=template_id)
            if distribution_id:
                distribution = get_object_or_404(models.Distribution, id=distribution_id)
                recipients = template.get_invitees(distribution)
            else:
                recipients = template.get_invitees()
            data["to"] = "; ".join(recipients)
        super(MailerFormBase, self).__init__(data, *args, **kwargs)

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
