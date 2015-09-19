# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refugeedata', '0007_auto_number_to_pk'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registrationnumber',
            old_name='id',
            new_name='uuid',
        ),
    ]
