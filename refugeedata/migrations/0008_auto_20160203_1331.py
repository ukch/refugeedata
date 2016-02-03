# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refugeedata', '0007_auto_20150921_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distribution',
            name='date',
            field=models.DateField(unique=True, verbose_name='Distribution Date'),
        ),
    ]
