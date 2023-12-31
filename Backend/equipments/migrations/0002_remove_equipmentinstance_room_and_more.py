# Generated by Django 4.2.7 on 2023-12-11 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipments', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipmentinstance',
            name='room',
        ),
        migrations.RemoveField(
            model_name='historicalequipmentinstance',
            name='room',
        ),
        migrations.AddField(
            model_name='equipment',
            name='category',
            field=models.CharField(choices=[('Glassware', 'Glassware'), ('Miscellaneous', 'Miscellaneous')], default='Miscellaneous', max_length=20),
        ),
        migrations.AddField(
            model_name='historicalequipment',
            name='category',
            field=models.CharField(choices=[('Glassware', 'Glassware'), ('Miscellaneous', 'Miscellaneous')], default='Miscellaneous', max_length=20),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='description',
            field=models.TextField(max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='historicalequipment',
            name='description',
            field=models.TextField(max_length=512, null=True),
        ),
    ]
