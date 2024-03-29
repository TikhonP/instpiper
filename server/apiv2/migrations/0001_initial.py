# Generated by Django 3.0.6 on 2020-06-20 21:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProxyV2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date')),
                ('proxy', models.TextField()),
                ('name', models.CharField(default='No Name', max_length=50)),
                ('health', models.IntegerField(default=101)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TokenV2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='No Name', max_length=50)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date')),
                ('token', models.CharField(max_length=40)),
                ('is_valid', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RequestV2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date')),
                ('data', models.TextField()),
                ('response', models.TextField(default=None, null=True)),
                ('is_done', models.IntegerField(default=0)),
                ('task_id', models.CharField(max_length=40)),
                ('is_id', models.BooleanField(default=False)),
                ('threads', models.IntegerField()),
                ('proxy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apiv2.ProxyV2')),
                ('token', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apiv2.TokenV2')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
