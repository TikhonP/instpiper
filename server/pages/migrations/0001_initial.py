# Generated by Django 3.0.6 on 2020-05-28 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('markdown_field', models.TextField()),
                ('html_field', models.TextField(editable=False)),
            ],
        ),
    ]
