# Generated by Django 4.2.7 on 2023-12-11 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('breakage', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='breakagereport',
            name='status',
        ),
        migrations.AddField(
            model_name='breakagereport',
            name='resolved',
            field=models.BooleanField(default=False),
        ),
    ]
