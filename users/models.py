from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# Create your models here.

class CustomUser(AbstractUser):
    class UserType(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        VENDOR = 'VENDOR', 'Vendor'
    user_type = models.CharField(max_length=10, choices=UserType.choices, default=UserType.CUSTOMER)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    certificate = models.ImageField(upload_to='certificates/', null=True, blank=True)
    store_open_time = models.TimeField(null=True, blank=True, default='10:00')
    store_close_time = models.TimeField(null=True, blank=True, default='22:00')
    bank_account_number = models.CharField(max_length=20, blank=True)
    bank_routing_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"