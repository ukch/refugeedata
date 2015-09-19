# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refugeedata', '0005_person_number_of_dependents'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='photo',
            field=models.ImageField(upload_to=b'user_images/%m%d%H%M%S/', null=True, verbose_name='Photo', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='preferred_contact',
            field=models.CharField(default=b'P', max_length=1, verbose_name='Preferred Contact', choices=[(b'P', 'SMS'), (b'E', 'Email')]),
        ),
    ]
