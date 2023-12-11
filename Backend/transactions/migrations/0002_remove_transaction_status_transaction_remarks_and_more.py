# Generated by Django 4.2.7 on 2023-12-11 10:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='status',
        ),
        migrations.AddField(
            model_name='transaction',
            name='remarks',
            field=models.TextField(max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teacher_transactions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='transaction',
            name='transaction_status',
            field=models.CharField(choices=[('Pending Approval', 'Pending Approval'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Cancelled', 'Cancelled'), ('Borrowed', 'Borrowed'), ('Returned: Pending Checking', 'Returned: Pending Checking'), ('With Breakage: Pending Resolution', 'With Breakage: Pending Resolution'), ('Finalized', 'Finalized')], default='Pending', max_length=40),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='borrower',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='borrowed_transactions', to=settings.AUTH_USER_MODEL),
        ),
    ]
