# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.management import call_command
from django.db import migrations

from django.contrib.sites.models import Site


fixture = 'initial_data'


def load_fixture(apps, schema_editor):
    call_command('loaddata', fixture, app_label='refugeedata')


def update_site(apps, schema_editor):
    if not settings.DEFAULT_DOMAIN:
        return
    site = Site.objects.all()[0]
    site.domain = settings.DEFAULT_DOMAIN
    site.save()


noop = migrations.RunPython.noop


class Migration(migrations.Migration):

    dependencies = [
        ('refugeedata', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=noop),
        migrations.RunPython(update_site, reverse_code=noop)
    ]
