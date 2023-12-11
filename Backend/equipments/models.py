from django.db import models
from django.utils.timezone import now
from simple_history.models import HistoricalRecords
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class Equipment(models.Model):
    EQUIPMENT_CATEGORY_CHOICES = (
        ('Glassware', 'Glassware'),
        ('Miscellaneous', 'Miscellaneous')
    )
    name = models.CharField(max_length=40)
    category = models.CharField(
        max_length=20, choices=EQUIPMENT_CATEGORY_CHOICES, default='Miscellaneous')
    description = models.TextField(max_length=512, null=True)
    date_added = models.DateTimeField(default=now, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.name} ID:{self.id}'


class EquipmentInstance(models.Model):
    EQUIPMENT_INSTANCE_STATUS_CHOICES = (
        ('Working', 'Working'),
        ('Broken', 'Broken'),
        ('Borrowed', 'Borrowed'),
    )
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=EQUIPMENT_INSTANCE_STATUS_CHOICES, default='PENDING')
    remarks = models.TextField(max_length=512, null=True)
    date_added = models.DateTimeField(default=now, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.equipment.name} ID:{self.id}'


@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    if sender.name == 'equipments':
        EQUIPMENT, CREATED = Equipment.objects.get_or_create(
            name="Pyrex Beaker", description="", category="Glassware")
        EQUIPMENT_INSTANCE, CREATED = EquipmentInstance.objects.get_or_create(
            equipment=EQUIPMENT, status="Working", remarks="First beaker of equipment tracker!")
        EQUIPMENT, CREATED = Equipment.objects.get_or_create(
            name="Bunsen Burner", description="", category="Miscellaneous")
        EQUIPMENT_INSTANCE, CREATED = EquipmentInstance.objects.get_or_create(
            equipment=EQUIPMENT, status="Working", remarks="First bunsen burner of equipment tracker!")
        EQUIPMENT, CREATED = Equipment.objects.get_or_create(
            name="Microscope", description="", category="Miscellaneous")
        EQUIPMENT_INSTANCE, CREATED = EquipmentInstance.objects.get_or_create(
            equipment=EQUIPMENT, status="Working", remarks="First microscope of equipment tracker!")
