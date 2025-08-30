from django.db import models

from .order import Order

class Invoice(models.Model):
    class InvoiceStatus(models.TextChoices):
        UNPAID = 'UNPAID', 'Unpaid'
        PAID = 'PAID', 'Paid'

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    # Todo: Total amount should be paid amount and order_total_amount?
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=InvoiceStatus.choices, default=InvoiceStatus.UNPAID)
    issued_at = models.DateTimeField(auto_now_add=True)
    commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Commission earned"
    )


    def __str__(self):
        return f"Invoice for Order {self.order.id}"


