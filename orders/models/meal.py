from django.conf import settings
from django.db import models


class Meal(models.Model):
    class TimeSlots(models.TextChoices):
        LUNCH_1200 = '12:00', '12:00 PM'
        LUNCH_1230 = '12:30', '12:30 PM'
        LUNCH_1300 = '13:00', '13:00 PM'
        DINNER_1800 = '18:00', '6:00 PM'
        DINNER_1830 = '18:30', '6:30 PM'

    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='meal_images/', blank=True, null=True)

    def __str__(self):
        return self.name
