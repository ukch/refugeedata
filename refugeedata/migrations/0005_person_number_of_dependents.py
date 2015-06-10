# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refugeedata', '0004_auto_20150516_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='number_of_dependents',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Number of Dependents'),
        ),
    ]
