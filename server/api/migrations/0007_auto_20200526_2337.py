# Generated by Django 3.0.6 on 2020-05-26 20:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0006_auto_20200526_2313'),
    ]

    operations = [
        migrations.AddField(
            model_name='req',
            name='is_id',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Proxy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date')),
                ('proxy', models.TextField()),
                ('name', models.CharField(default='No Name', max_length=50)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
