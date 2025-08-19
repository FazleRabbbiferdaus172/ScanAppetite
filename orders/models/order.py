from django.conf import settings
from django.db import models


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=OrderStatus.choices, default=OrderStatus.DRAFT)

    def __str__(self):
        return f"Order {self.id} by {self.customer.username}"
