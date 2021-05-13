# -*- coding: utf-8 -*-


from django.db import models, migrations
import uuidfield.fields
import refugeedata.models


class Migration(migrations.Migration):

    dependencies = [
        ('refugeedata', '0006_auto_20150919_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationnumber',
            name='short_id_missing',
            field=models.BooleanField(default=False, verbose_name='short ID missing'),
        ),
        migrations.AlterField(
            model_name='registrationnumber',
            name='id',
            field=uuidfield.fields.UUIDField(primary_key=True, default=refugeedata.models.manual_uuid_generation, serialize=False, editable=False, max_length=32, blank=True, unique=True, verbose_name='ID'),
        ),
    ]
