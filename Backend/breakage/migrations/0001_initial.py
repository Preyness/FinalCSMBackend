# Generated by Django 4.2.7 on 2023-11-29 14:44

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('transactions', '0001_initial'),
        ('equipments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BreakageReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('REIMBURSED', 'Reimbursed'), ('REPLACED', 'Replaced')], default='PENDING', max_length=20)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('equipments', models.ManyToManyField(to='equipments.equipmentinstance')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transactions.transaction')),
            ],
        ),
    ]
