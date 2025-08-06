import pytz
from django.utils import timezone
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
    TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.common_timezones]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    certificate = models.ImageField(upload_to='certificates/', null=True, blank=True)
    store_open_time = models.TimeField(null=True, blank=True, default='10:00')
    store_close_time = models.TimeField(null=True, blank=True, default='22:00')
    bank_account_number = models.CharField(max_length=20, blank=True)
    bank_routing_number = models.CharField(max_length=20, blank=True)
    is_approved = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default=settings.TIME_ZONE)

    @property
    def is_open(self):
        """
        Calculates if the store is currently open based on its opening/closing times and timezone.
        """
        if not self.store_open_time or not self.store_close_time:
            return False

        try:
            # Use the vendor's timezone; if not set, use the project's default TIME_ZONE.
            vendor_tz_str = self.timezone or settings.TIME_ZONE
            vendor_tz = pytz.timezone(vendor_tz_str)
        except pytz.UnknownTimeZoneError:
            # Fallback to UTC as a last resort.
            vendor_tz = pytz.utc

        # Get the current time and convert it to the vendor's local timezone
        vendor_local_time = timezone.now().astimezone(vendor_tz).time()
        
        open_time = self.store_open_time
        close_time = self.store_close_time
        
        # Handle overnight hours
        if open_time > close_time:
            # Store is open if current time is after open time OR before close time
            return vendor_local_time >= open_time or vendor_local_time <= close_time
        else:
            # Normal same-day hours
            return open_time <= vendor_local_time <= close_time

    def __str__(self):
        return f"{self.user.username}'s Profile"