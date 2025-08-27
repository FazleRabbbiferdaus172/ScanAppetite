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
    commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Commission earned from the vendor for this order"
    )


    def __str__(self):
        return f"Order {self.id} by {self.customer.username}"
