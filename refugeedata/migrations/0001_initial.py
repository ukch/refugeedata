# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields


class Migration(migrations.Migration):

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
        migrations.CreateModel(
            name='RegistrationCardBatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pdf', models.FileField(upload_to=b'')),
                ('registration_numbers', models.ManyToManyField(to=b'refugeedata.RegistrationNumber')),
            ],
            options={
                'verbose_name_plural': 'Registration card batches',
            },
        ),
        migrations.CreateModel(
            name='RegistrationCardBatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pdf', models.FileField(upload_to=b'')),
                ('registration_numbers', models.ManyToManyField(to=b'refugeedata.RegistrationNumber')),
            ],
            options={
                'verbose_name_plural': 'Registration card batches',
            },
        ),
    ]
