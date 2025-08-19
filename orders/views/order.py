from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from orders.models import OrderItem, Order
from users.mixins import VendorRequiredMixin


@login_required
def order_confirmation_view(request):
    # This view just renders the "thank you" template
    return render(request, 'orders/order_confirmation.html')


@login_required
def update_order_item_status_view(request, item_id):
    # Security: Ensure user is a vendor and this item belongs to them
    item = get_object_or_404(OrderItem, id=item_id, meal__vendor=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        if new_status in OrderItem.FulfillmentStatus.values:
            item.status = new_status
            item.save()

    return redirect('vendor_dashboard')


@login_required
def order_history_view(request):
    if request.user.user_type != 'CUSTOMER':
        return redirect('homepage')

    orders = Order.objects.filter(customer=request.user).prefetch_related(
        'items__meal'
    ).order_by('-created_at')

    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def cancel_order_view(request, order_id):
    # Security: Get the order, ensuring it belongs to the logged-in customer and is in Draft state
    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user,
        status=Order.OrderStatus.DRAFT
    )

    if request.method == 'POST':
        order.status = Order.OrderStatus.CANCELLED
        order.save()
        messages.success(request, f"Order #{order.id} has been cancelled.")
        return redirect('order_history')

    # If GET request, you could render a confirmation template, but for simplicity, we redirect.
    return redirect('order_history')


class VendorOrderHistoryView(LoginRequiredMixin, VendorRequiredMixin, ListView):
    model = OrderItem
    template_name = 'orders/vendor_order_history.html'
    context_object_name = 'historical_items'

    def get_queryset(self):
        # Fetch items that belong to the vendor from completed or cancelled orders
        return OrderItem.objects.filter(
            meal__vendor=self.request.user,
            status__in=[
                OrderItem.FulfillmentStatus.DELIVERED,
                # You could add a 'CANCELLED' status later if needed
            ]
        ).order_by('-order__created_at')


@login_required
def confirm_pickup_view(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)

    # Security check: only the customer for this order can confirm pickup
    if request.method == 'POST' and request.user == item.order.customer:
        if item.status == OrderItem.FulfillmentStatus.READY_FOR_PICKUP:
            item.status = OrderItem.FulfillmentStatus.DELIVERED
            item.save()
            messages.success(request, f"Pickup confirmed for '{item.meal.name}'.")
        else:
            messages.error(request, "This item is not ready for pickup.")

    return redirect('order_history')
