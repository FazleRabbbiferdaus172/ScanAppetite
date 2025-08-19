from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from orders.models import OrderItem


@login_required
def update_item_status(request, item_id, new_status):
    # Security: Ensure user is a vendor and this item belongs to them
    item = get_object_or_404(OrderItem, id=item_id, meal__vendor=request.user)

    # Check if the requested status is a valid choice
    if new_status in OrderItem.FulfillmentStatus.values:
        item.status = new_status
        item.save()
        messages.success(request, f"Status for '{item.meal.name}' updated.")
    else:
        messages.error(request, "Invalid status.")

    dashboard_url = reverse('vendor_dashboard')
    redirect_url = f'{dashboard_url}#item-row-{item_id}'
    return redirect(redirect_url)