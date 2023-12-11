from django.db import models
from accounts.models import CustomUser
from transactions.models import Transaction
from equipments.models import EquipmentInstance
from django.utils.timezone import now


class BreakageReport(models.Model):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE)
    equipments = models.ManyToManyField(EquipmentInstance)
    resolved = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        return f"Breakage report for transaction #{self.transaction.id} by {self.transaction.borrower} under {self.transaction.teacher}"

    def save(self, *args, **kwargs):
        # Check if the instance is being updated
        if not self._state.adding:
            # Check if all associated equipment instances have status "Working"
            all_working = all(
                eq.status == 'Working' for eq in self.equipments.all())

            # If all equipment instances are working
            if all_working:
                # set resolved field to True
                self.resolved = True
                # set the status of the associated transaction to "Finalized"
                self.transaction.status = 'Finalized'
                self.transaction.save()

                # Then save the instance again to reflect the changes
                super().save(*args, **kwargs)
            # If not, set the resolved field to False
            else:
                if (self.resolved != False or self.transaction.status != 'With Breakages: Pending Resolution'):
                    # set resolved field to False
                    self.resolved = False
                    # set the status of the associated transaction to still be pending
                    self.transaction.status = 'With Breakages: Pending Resolution'
                    self.transaction.save()
                    # Then save the instance again to reflect the changes
                    super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
