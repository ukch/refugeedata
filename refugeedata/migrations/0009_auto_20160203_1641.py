# -*- coding: utf-8 -*-


import logging

from django.db import migrations
import imagekit.models.fields


def apply_change(apps, schema_editor):
    Person = apps.get_model("refugeedata", "Person")
    if Person.objects.count() > 1000:
        logging.warn("There are too many people in your database for this migration to run. Please run manage.py rotate_and_scale_images instead.")
        return
    for person in Person.objects.all():
        if person.photo:
            person.photo.save(person.photo.name, person.photo.file)


class Migration(migrations.Migration):

    dependencies = [
        ('refugeedata', '0008_auto_20160203_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='photo',
            field=imagekit.models.fields.ProcessedImageField(upload_to=b'user_images/%m%d%H%M%S/', null=True, verbose_name='Photo', blank=True),
        ),
        migrations.RunPython(apply_change, reverse_code=migrations.RunPython.noop),
    ]
