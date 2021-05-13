# -*- coding: utf-8 -*-


from django.db import migrations, models
import django_extras.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('refugeedata', '0010_auto_20160211_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='attendance_percent',
            field=django_extras.db.models.fields.PercentField(null=True, verbose_name='Distribution attendance', blank=True),
        ),
    ]
