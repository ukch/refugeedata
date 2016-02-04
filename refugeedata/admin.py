from django.core.management import call_command
from django.contrib import admin

from refugeedata import models, forms


class DistributionAdmin(admin.ModelAdmin):

    list_display = ("date", "supplies_quantity", "supplies_description")
    form = forms.DistributionAdminForm


class PersonAdmin(admin.ModelAdmin):

    list_display = ("name", "preferred_lang", "registration_card", "phone",
                    "active", "photo")
    search_fields = ("name", "needs", "email", "phone")
    form = forms.PersonAdminForm


class NumberAdmin(admin.ModelAdmin):

    list_display = ("number", "short_id", "active")


class BatchAdmin(admin.ModelAdmin):

    list_display = ("registration_number_format", "data_file")

    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            kwargs["form"] = forms.BatchAdminForm
        return super(BatchAdmin, self).get_form(request, obj=obj, **kwargs)

    def save_related(self, request, form, formsets, change):
        if not change:  # create
            numbers = form.cleaned_data["registration_numbers"]
            models.RegistrationNumber.objects.bulk_create(numbers)
            form.cleaned_data["registration_numbers"] = (
                models.RegistrationNumber.objects.filter(
                    id__in=[n.id for n in numbers]))
        super(BatchAdmin, self).save_related(request, form, formsets, change)
        call_command("export_card_data", str(form.instance.id), "--save")


class LanguageAdmin(admin.ModelAdmin):

    list_display = ("iso_code", "description", "example_text")


class TemplateAdmin(admin.ModelAdmin):

    list_display = ("text", "language", "type")
    form = forms.TemplateAdminForm


admin.site.register(models.Distribution, DistributionAdmin)
admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.Language, LanguageAdmin)
admin.site.register(models.RegistrationCardBatch, BatchAdmin)
admin.site.register(models.RegistrationNumber, NumberAdmin)
admin.site.register(models.Template, TemplateAdmin)
