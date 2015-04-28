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
                ('pdf', models.FileField(null=True, upload_to=b'', blank=True)),
                ('registration_numbers', models.ManyToManyField(to=b'refugeedata.RegistrationNumber')),
            ],
            options={
                'verbose_name_plural': 'Registration card batches',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('iso_code', models.CharField(max_length=b'5')),
                ('description', models.CharField(max_length=255)),
                ('example_text', models.CharField(max_length=255)),
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
                ('story', models.TextField(null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('photo', models.ImageField(null=True, upload_to=b'', blank=True)),
                ('preferred_lang', models.ForeignKey(verbose_name='Preferred language', to='refugeedata.Language')),
                ('registration_card', models.OneToOneField(null=True, blank=True, to='refugeedata.RegistrationNumber')),
                ('preferred_contact', models.CharField(default=b'E', max_length=1, choices=[(b'P', 'Phone'), (b'E', 'Email')])),
            ],
        ),
        migrations.AlterField(
            model_name='language',
            name='example_text',
            field=models.TextField(max_length=255),
        ),
    ]
