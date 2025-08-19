from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from django.contrib import messages
from django.db.models import Sum, Count

from orders.models import OrderItem, Meal, Order
from users.mixins import VendorRequiredMixin
from users.models import CustomUser


class VendorDashboardView(LoginRequiredMixin, VendorRequiredMixin, TemplateView):
    template_name = 'orders/vendor_dashboard.html'

    def get_context_data(self, **kwargs):
        # Get the default context
        context = super().get_context_data(**kwargs)
        vendor = self.request.user

        profile = getattr(vendor, 'profile', None)
        if not profile or not profile.bank_account_number:
            messages.warning(self.request,
                             "Your store is inactive. Please add your bank details in 'My Store' to activate it.")

        delivered_items = OrderItem.objects.filter(
            meal__vendor=vendor,
            status=OrderItem.FulfillmentStatus.DELIVERED
        )
        total_revenue = sum(item.meal.price * item.quantity for item in delivered_items)

        # 2. Calculate Total Meals Sold
        total_meals_sold = delivered_items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

        # 3. Find Most Popular Meals
        # We group by meal name and count how many times each has been ordered.
        popular_meals = OrderItem.objects.filter(meal__vendor=vendor).values(
            'meal__name'
        ).annotate(
            order_count=Count('id')
        ).order_by('-order_count')[:5]  # Get top 5

        # Add statistics to the context
        context['total_revenue'] = total_revenue
        context['total_meals_sold'] = total_meals_sold
        context['popular_meals'] = popular_meals

        # Get the list of meals for this vendor
        context['meals'] = Meal.objects.filter(vendor=self.request.user)

        # Get the list of active order items for this vendor
        context['order_items'] = OrderItem.objects.filter(
            meal__vendor=self.request.user,
            order__status=Order.OrderStatus.CONFIRMED,
            order__is_paid=True
        ).exclude(
            status=OrderItem.FulfillmentStatus.DELIVERED
        ).order_by('order__created_at')

        order_items = OrderItem.objects.filter(
            meal__vendor=self.request.user,
            order__status=Order.OrderStatus.CONFIRMED,
            order__is_paid=True
        ).exclude(
            status=OrderItem.FulfillmentStatus.DELIVERED
        ).order_by('order__created_at')

        context['has_ready_items'] = any(
            item.status == OrderItem.FulfillmentStatus.READY_FOR_PICKUP
            for item in order_items
        )

        return context


def vendor_detail_view(request, vendor_id):
    vendor = get_object_or_404(CustomUser, id=vendor_id, user_type='VENDOR')
    meals = Meal.objects.filter(vendor=vendor)
    profile = getattr(vendor, 'profile', None)  # Safely get profile

    # Default values
    is_open = False
    store_is_active = False

    if profile:
        store_is_active = bool(profile.bank_account_number)
        # Use the new, timezone-aware property from the model
        is_open = profile.is_open

    context = {
        'vendor': vendor,
        'meals': meals,
        'is_open': is_open,
        'store_is_active': store_is_active,
    }
    return render(request, 'orders/vendor_detail.html', context)
