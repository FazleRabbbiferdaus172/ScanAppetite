import uuid
from datetime import date

from django.db import models

from .order import Order
from .meal import Meal

class OrderItem(models.Model):
    class FulfillmentStatus(models.TextChoices):
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        PROCESSING = 'PROCESSING', 'Processing'
        READY_FOR_PICKUP = 'READY_FOR_PICKUP', 'Ready for Pickup'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=FulfillmentStatus.choices, default=FulfillmentStatus.CONFIRMED)
    preferred_delivery_time = models.DateTimeField(null=True, blank=True)
    barcode_id = models.UUIDField(default=uuid.uuid4, editable=False)
    pickup_date = models.DateField(default=date.today)
    pickup_time = models.CharField(default=Meal.TimeSlots.LUNCH_1200, max_length=10, choices=Meal.TimeSlots.choices)

    def __str__(self):
        return f"{self.quantity} of {self.meal.name}"
