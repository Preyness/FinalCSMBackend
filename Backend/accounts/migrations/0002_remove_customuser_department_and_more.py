# Generated by Django 4.2.7 on 2023-11-27 04:58

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='department',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='is_labtech',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='is_teacher',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='middle_name',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='verified_faculty',
        ),
        migrations.AddField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(null=True, upload_to=accounts.models.CustomUser._get_upload_to),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]