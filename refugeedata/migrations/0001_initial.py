# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields


class Migration(migrations.Migration):

    replaces = [(b'refugeedata', '0001_initial'), (b'refugeedata', '0002_remove_registrationnumber_assigned')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationNumber',
            fields=[
                ('id', uuidfield.fields.UUIDField(primary_key=True, serialize=False, editable=False, max_length=32, blank=True, unique=True)),
                ('number', models.PositiveSmallIntegerField()),
                ('active', models.BooleanField(default=False)),
            ],
        ),
    ]
