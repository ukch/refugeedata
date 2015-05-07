# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('iso_code', models.CharField(max_length=b'5')),
                ('description', models.CharField(max_length=255)),
                ('example_text', models.TextField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('needs', models.TextField(null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('phone', models.CharField(max_length=20, null=True, blank=True)),
                ('preferred_contact', models.CharField(default=b'E', max_length=1, choices=[(b'P', 'Phone'), (b'E', 'Email')])),
                ('story', models.TextField(null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('photo', models.ImageField(null=True, upload_to=b'', blank=True)),
                ('preferred_lang', models.ForeignKey(verbose_name='Preferred language', to='refugeedata.Language')),
            ],
        ),
        migrations.CreateModel(
            name='RegistrationCardBatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pdf', models.FileField(null=True, upload_to=b'', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Registration card batches',
            },
        ),
        migrations.CreateModel(
            name='RegistrationNumber',
            fields=[
                ('id', uuidfield.fields.UUIDField(primary_key=True, serialize=False, editable=False, max_length=32, blank=True, unique=True)),
                ('number', models.PositiveSmallIntegerField()),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('number',),
            },
        ),
        migrations.AddField(
            model_name='registrationcardbatch',
            name='registration_numbers',
            field=models.ManyToManyField(to='refugeedata.RegistrationNumber'),
        ),
        migrations.AddField(
            model_name='person',
            name='registration_card',
            field=models.OneToOneField(null=True, blank=True, to='refugeedata.RegistrationNumber'),
        ),
    ]
