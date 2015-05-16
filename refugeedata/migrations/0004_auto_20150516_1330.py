# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refugeedata', '0003_auto_20150513_1147'),
    ]

    operations = [
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='Distribution Date')),
                ('supplies_quantity', models.SmallIntegerField(verbose_name='Supplies Quantity')),
                ('supplies_description', models.TextField(null=True, verbose_name='Supplies Description', blank=True)),
                ('finish_number', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('attendees', models.ManyToManyField(related_name='distributions_attended', to='refugeedata.RegistrationNumber', blank=True)),
                ('invitees', models.ManyToManyField(related_name='distributions_invited_to', to='refugeedata.RegistrationNumber')),
            ],
            options={
                'ordering': ('date',),
                'verbose_name': 'Distribution',
                'verbose_name_plural': 'Distributions',
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=1, verbose_name='Template Type', choices=[(b'P', 'SMS'), (b'E', 'Email')])),
                ('text', models.TextField(verbose_name='Template Text')),
                ('language', models.ForeignKey(verbose_name='Language', to='refugeedata.Language')),
            ],
            options={
                'verbose_name': 'Template',
                'verbose_name_plural': 'Templates',
            },
        ),
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ('registration_card__number',), 'verbose_name': 'Person', 'verbose_name_plural': 'People'},
        ),
        migrations.AlterField(
            model_name='person',
            name='photo',
            field=models.ImageField(upload_to=b'user_images', null=True, verbose_name='Photo', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='preferred_contact',
            field=models.CharField(default=b'E', max_length=1, verbose_name='Preferred Contact', choices=[(b'P', 'SMS'), (b'E', 'Email')]),
        ),
        migrations.AlterField(
            model_name='registrationcardbatch',
            name='data_file',
            field=models.FileField(upload_to=b'card_data', null=True, verbose_name='Data File', blank=True),
        ),
        migrations.AddField(
            model_name='distribution',
            name='templates',
            field=models.ManyToManyField(to='refugeedata.Template', verbose_name='Templates'),
        ),
    ]
