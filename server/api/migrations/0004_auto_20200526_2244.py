# Generated by Django 3.0.6 on 2020-05-26 19:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20200525_2358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='req',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 26, 22, 44, 49, 705973), verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='token',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 26, 22, 44, 49, 705563), verbose_name='Date'),
        ),
    ]
