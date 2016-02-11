# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refugeedata', '0009_auto_20160203_1641'),
    ]

    operations = [
        migrations.CreateModel(
            name='DistributionTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
            options={
                'ordering': ('start_time',),
            },
        ),
        migrations.AddField(
            model_name='distribution',
            name='times',
            field=models.ManyToManyField(to='refugeedata.DistributionTime', verbose_name='Distribution Times', blank=True),
        ),
    ]
