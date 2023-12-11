from django.db import models
from accounts.models import CustomUser
from equipments.models import EquipmentInstance
from django.utils.timezone import now


class Transaction(models.Model):
    TRANSACTION_STATUS_CHOICES = (
        # Transaction is pending approval
        ('Pending Approval', 'Pending Approval'),
        # Transaction has been approved, pending delivery by labtech
        ('Approved', 'Approved'),
        # Tranasction has been rejected
        ('Rejected', 'Rejected'),
        # Transaction has been approved but has been cancelled due to rare circumstances
        ('Cancelled', 'Cancelled'),
        # Transaction has been delivered and is on borrow
        ('Borrowed', 'Borrowed'),
        # Transaction has been returned, pending checking
        ('Returned: Pending Checking', 'Returned: Pending Checking'),
        # Transaction has been breakages after being returned, pending resolution
        ('With Breakage: Pending Resolution',
            'With Breakage: Pending Resolution'),
        # Transaction has been finalized
        ('Finalized', 'Finalized'),
    )

    borrower = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name='borrowed_transactions')
    remarks = models.TextField(max_length=512, null=True)
    teacher = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name='teacher_transactions')
    equipments = models.ManyToManyField(EquipmentInstance)
    transaction_status = models.CharField(
        max_length=40, choices=TRANSACTION_STATUS_CHOICES, default='Pending')
    timestamp = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        return f"Transaction #{self.id} under {self.teacher} by {self.borrower}"
