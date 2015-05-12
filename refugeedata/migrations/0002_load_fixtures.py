# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management import call_command
from django.db import migrations


fixture = 'initial_data'


def load_fixture(apps, schema_editor):
    call_command('loaddata', fixture, app_label='refugeedata')


noop = migrations.RunPython.noop


class Migration(migrations.Migration):

    dependencies = [
        ('refugeedata', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=noop),
    ]
