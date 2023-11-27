from django.db import models
from accounts.models import CustomUser
from equipments.models import EquipmentInstance
from django.utils.timezone import now

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('APPROVED', 'Approved'),
        ('RETURNED', 'Returned'),
        ('REJECTED', 'Rejected'),
        ('PENDING', 'Pending'),
    )

    borrower = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True)
    equipments = models.ManyToManyField(EquipmentInstance)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='PENDING')
    timestamp = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        return f"Transaction by {self.borrower}"