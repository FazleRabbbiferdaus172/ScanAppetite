from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, TemplateView
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import barcode
from barcode.writer import ImageWriter, SVGWriter
from io import BytesIO
from django.http import HttpResponse
from .models import Meal, Order, OrderItem, Invoice
from .forms import MealForm


def homepage_view(request):
    # If the user is logged in AND is a vendor
    if request.user.is_authenticated and request.user.user_type == 'VENDOR':
        # Redirect them to their dashboard
        return redirect('vendor_dashboard')

    # Otherwise, show the normal meal list page to customers and anonymous users
    meals = Meal.objects.all()
    context = {'meals': meals}
    return render(request, 'orders/meal_list.html', context)


class MealListView(ListView):
    model = Meal
    template_name = 'orders/meal_list.html'
    context_object_name = 'meals'  # The name of the variable in the template


class VendorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'VENDOR'


# View for the Vendor's Dashboard (lists their own meals)
class VendorDashboardView(LoginRequiredMixin, VendorRequiredMixin, TemplateView):
    template_name = 'orders/vendor_dashboard.html'

    def get_context_data(self, **kwargs):
        # Get the default context
        context = super().get_context_data(**kwargs)

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

        return context


# View for creating a new meal
class MealCreateView(LoginRequiredMixin, VendorRequiredMixin, CreateView):
    model = Meal
    form_class = MealForm
    template_name = 'orders/meal_form.html'
    success_url = reverse_lazy('vendor_dashboard')

    def form_valid(self, form):
        # Automatically set the logged-in user as the vendor
        form.instance.vendor = self.request.user
        return super().form_valid(form)


# View for updating an existing meal
class MealUpdateView(LoginRequiredMixin, VendorRequiredMixin, UpdateView):
    model = Meal
    form_class = MealForm
    template_name = 'orders/meal_form.html'
    success_url = reverse_lazy('vendor_dashboard')

    def get_queryset(self):
        # Ensure vendors can only edit their own meals
        return Meal.objects.filter(vendor=self.request.user)


# View for deleting a meal
class MealDeleteView(LoginRequiredMixin, VendorRequiredMixin, DeleteView):
    model = Meal
    template_name = 'orders/meal_confirm_delete.html'
    success_url = reverse_lazy('vendor_dashboard')

    def get_queryset(self):
        # Ensure vendors can only delete their own meals
        return Meal.objects.filter(vendor=self.request.user)


def add_to_cart(request, meal_id):
    # meal = get_object_or_404(Meal, id=meal_id)
    # Get the cart from the session, or create an empty one
    meal = get_object_or_404(Meal, id=meal_id)
    cart = request.session.get('cart', {})

    # Add the meal to the cart or increment its quantity
    meal_id_str = str(meal_id)
    quantity = cart.get(meal_id_str, 0) + 1
    cart[meal_id_str] = quantity

    # Save the updated cart back to the session
    request.session['cart'] = cart
    messages.success(request, f"{meal.name} was added to your cart.")
    return redirect('homepage')


@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for meal_id, quantity in cart.items():
        meal = get_object_or_404(Meal, id=int(meal_id))
        item_total = meal.price * quantity
        cart_items.append({'meal': meal, 'quantity': quantity, 'total': item_total})
        total_price += item_total

    return render(request, 'orders/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('homepage')

    order = Order.objects.create(customer=request.user, status=Order.OrderStatus.DRAFT)

    total_price = 0
    for meal_id, quantity in cart.items():
        meal = get_object_or_404(Meal, id=int(meal_id))
        OrderItem.objects.create(order=order, meal=meal, quantity=quantity)
        total_price += meal.price * quantity

    invoice = Invoice.objects.create(order=order, total_amount=total_price)

    request.session['cart'] = {}

    return redirect('invoice_detail', order_id=order.id)


@login_required
def invoice_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'orders/invoice_detail.html', {'order': order})


@login_required
def process_payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    # In a real app, payment processing logic (e.g., Stripe) would go here.
    # For now, we'll simulate a successful payment.

    if hasattr(order, 'invoice'):
        order.invoice.status = Invoice.InvoiceStatus.PAID
        order.invoice.save()

    # Update the order status to CONFIRMED
    order.status = Order.OrderStatus.CONFIRMED
    order.is_paid = True
    order.save()

    return redirect('order_confirmation')


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
    # Ensure the user is a customer
    if request.user.user_type != 'CUSTOMER':
        return redirect('homepage')

    # Fetch all orders placed by this customer, ordering by the most recent
    # Prefetch the related items and meals to avoid extra database queries
    orders = Order.objects.filter(customer=request.user).prefetch_related(
        'items__meal'
    ).order_by('-created_at')

    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def view_item_barcode(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    # Security check
    if request.user != item.order.customer and request.user != item.meal.vendor:
        return HttpResponse("Unauthorized", status=403)

    Code128 = barcode.get_barcode_class('code128')
    # Use the item's unique barcode_id as the data
    # Change the writer to SVGWriter()
    code = Code128(str(item.barcode_id), writer=SVGWriter())

    buffer = BytesIO()
    code.write(buffer)

    buffer.seek(0)

    # Return the buffer as an SVG image
    return HttpResponse(buffer.getvalue(), content_type='image/svg+xml')


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

