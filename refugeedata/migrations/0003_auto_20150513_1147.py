# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refugeedata', '0002_load_fixtures'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registrationcardbatch',
            name='pdf',
        ),
        migrations.AddField(
            model_name='registrationcardbatch',
            name='data_file',
            field=models.FileField(upload_to=b'', null=True, verbose_name='Data File', blank=True),
        ),
    ]
