from django.db import models
from accounts.models import CustomUser
from transactions.models import Transaction
from equipments.models import EquipmentInstance
from django.utils.timezone import now
# Create your models here.
#


class BreakageReport(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('REIMBURSED', 'Reimbursed'),
        ('REPLACED', 'Replaced'),
    )

    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE)
    equipments = models.ManyToManyField(EquipmentInstance)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='PENDING')
    timestamp = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        return f"Breakage report for transaction {self.borrower}"
