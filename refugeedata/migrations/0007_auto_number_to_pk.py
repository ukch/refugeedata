# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('refugeedata', '0006_auto_inconsequential'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrationnumber',
            name='number',
            field=models.PositiveSmallIntegerField(serialize=False, verbose_name='number', primary_key=True),
        ),
        migrations.AlterField(
            model_name='registrationnumber',
            name='id',
            field=uuidfield.fields.UUIDField(verbose_name='ID', unique=True, max_length=32, editable=False, blank=True),
        ),
    ]
