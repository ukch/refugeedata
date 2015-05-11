from django.contrib import admin

from refugeedata import models, forms


class NumberAdmin(admin.ModelAdmin):

    list_display = ("number", "short_id", "active")


class BatchAdmin(admin.ModelAdmin):

    list_display = ("registration_number_format", "pdf")

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
        return super(BatchAdmin, self).save_related(
            request, form, formsets, change)


class LanguageAdmin(admin.ModelAdmin):

    list_display = ("iso_code", "description", "example_text")


admin.site.register(models.RegistrationNumber, NumberAdmin)
admin.site.register(models.RegistrationCardBatch, BatchAdmin)
admin.site.register(models.Language, LanguageAdmin)
