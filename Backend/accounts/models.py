from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import os


class CustomUser(AbstractUser):

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    verified_faculty = models.BooleanField(default=False)
    is_labtech = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    pass

# automatic mag create og superuser didto ra kuhaon sa .env


@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    if sender.name == 'accounts':
        User = CustomUser
        username = os.getenv('DJANGO_ADMIN_USERNAME')
        email = os.getenv('DJANGO_ADMIN_EMAIL')
        password = os.getenv('DJANGO_ADMIN_PASSWORD')

        if not User.objects.filter(username=username).exists():
            # Create the superuser with is_active set to False
            superuser = User.objects.create_superuser(
                username=username, email=email, password=password, is_labtech=True, verified_faculty=True)

            # Activate the superuser
            superuser.is_active = True
            print('Created admin account')
            superuser.save()
