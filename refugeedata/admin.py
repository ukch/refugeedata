from django.contrib import admin

from refugeedata import models


"""class RegistrationNumberInline(admin.TabularInline):

    model = models.RegistrationNumber
    """


class NumberAdmin(admin.ModelAdmin):

    list_display = ("number", "id", "active")
    #actions = [foo]


class BatchAdmin(admin.ModelAdmin):

    list_display = ("registration_number_format", "pdf")


class LanguageAdmin(admin.ModelAdmin):

    list_display = ("iso_code", "description", "example_text")


admin.site.register(models.RegistrationNumber, NumberAdmin)
admin.site.register(models.RegistrationCardBatch, BatchAdmin)
admin.site.register(models.Language, LanguageAdmin)
