from datetime import date
from django.conf import settings
from django.db import models
import uuid

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
    pickup_time = models.CharField(default = Meal.TimeSlots.LUNCH_1200, max_length=10, choices=Meal.TimeSlots.choices)

    def __str__(self):
        return f"{self.quantity} of {self.meal.name}"
    

class Invoice(models.Model):
    class InvoiceStatus(models.TextChoices):
        UNPAID = 'UNPAID', 'Unpaid'
        PAID = 'PAID', 'Paid'

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=InvoiceStatus.choices, default=InvoiceStatus.UNPAID)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice for Order {self.order.id}"
    

