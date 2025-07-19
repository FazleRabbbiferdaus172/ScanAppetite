import uuid
import json
import barcode
from collections import defaultdict
from io import BytesIO
from barcode.writer import ImageWriter, SVGWriter
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import Meal, Order, OrderItem, Invoice
from users.models import CustomUser
from .forms import MealForm


def homepage_view(request):
    if request.user.is_authenticated and request.user.user_type == 'VENDOR':
        return redirect('vendor_dashboard')

    vendors_with_meals = defaultdict(list)
    meals = Meal.objects.select_related('vendor').all()
    for meal in meals:
        vendors_with_meals[meal.vendor].append(meal)

    context = {'vendors_with_meals': dict(vendors_with_meals)}
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
    meal = get_object_or_404(Meal, id=meal_id)
    # Get the cart from the session, or create an empty list
    cart = request.session.get('cart', [])

    # Create a new, unique item for the cart
    cart_item = {
        'cart_item_id': str(uuid.uuid4()),  # A unique ID for this specific cart item
        'meal_id': meal_id,
        'meal_name': meal.name,
        'price': float(meal.price)  # Store price in case it changes later
    }

    # Append the new item to the cart list
    cart.append(cart_item)

    request.session['cart'] = cart
    messages.success(request, f"{meal.name} was added to your cart.")

    return redirect(request.META.get('HTTP_REFERER', 'homepage'))


@login_required
def view_cart(request):
    cart = request.session.get('cart', [])
    total_price = sum(item['price'] for item in cart)
    tomorrow = date.today() + timedelta(days=1)

    return render(request, 'orders/cart_detail.html', {
        'cart_items': cart,
        'total_price': total_price,
        'meal_model': Meal,
        'default_pickup_date': tomorrow.isoformat()
    })

@login_required
def checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('homepage')

        order = Order.objects.create(customer=request.user, status=Order.OrderStatus.DRAFT)
        total_price = 0

        # Loop through the items that are in the session cart
        for item_data in cart:
            cart_item_id = item_data['cart_item_id']
            meal = get_object_or_404(Meal, id=item_data['meal_id'])

            # Get the date and time for this specific cart item from the form
            pickup_date_str = request.POST.get(f'pickup_date_{cart_item_id}')
            pickup_time = request.POST.get(f'pickup_time_{cart_item_id}')

            # Basic validation
            # ... (Add your date validation logic here) ...

            # Create an OrderItem with quantity=1 for each item in the cart
            OrderItem.objects.create(
                order=order,
                meal=meal,
                quantity=1,  # Quantity is always 1 now
                pickup_date=pickup_date_str,
                pickup_time=pickup_time
            )
            total_price += meal.price

        Invoice.objects.create(order=order, total_amount=total_price)
        request.session['cart'] = []  # Clear the cart list

        return redirect('invoice_detail', order_id=order.id)

    return redirect('view_cart')


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

    try:
        import qrcode
        import qrcode.image.svg

        # Create a QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # Add the item's unique barcode_id as the data
        qr.add_data(str(item.barcode_id))
        qr.make(fit=True)

        # Create an SVG image from the QR Code instance
        img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)

        # Write to a buffer
        buffer = BytesIO()
        img.save(buffer)
        buffer.seek(0)

        return HttpResponse(buffer.getvalue(), content_type='image/svg+xml')

    except ImportError:
        # Fallback or error message if qrcode library is missing
        return HttpResponse("QR Code generation library is not installed.", status=500)


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


def vendor_detail_view(request, vendor_id):
    vendor = get_object_or_404(CustomUser, id=vendor_id, user_type='VENDOR')
    meals = Meal.objects.filter(vendor=vendor)
    return render(request, 'orders/vendor_detail.html', {'vendor': vendor, 'meals': meals})


@login_required
def printable_barcode_view(request, item_id):
    # Security: Ensure user is a vendor and this item belongs to them
    item = get_object_or_404(OrderItem, id=item_id, meal__vendor=request.user)
    return render(request, 'orders/printable_barcode.html', {'item': item})


@login_required
def print_bulk_barcodes_view(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids')

        # Security: Fetch only items that belong to the logged-in vendor
        items = OrderItem.objects.filter(
            id__in=item_ids,
            meal__vendor=request.user,
            status=OrderItem.FulfillmentStatus.READY_FOR_PICKUP
        )

        return render(request, 'orders/printable_bulk_barcodes.html', {'items': items})

    return redirect('vendor_dashboard')


@login_required
def qr_code_scanner_view(request):
    # This view just renders the scanner template
    return render(request, 'orders/qr_code_scanner.html')


@login_required
def scan_and_verify_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            barcode_id = data.get('barcode_id')

            # Find the order item with this barcode ID, ensuring it belongs to the current user
            item = OrderItem.objects.get(
                barcode_id=barcode_id,
                order__customer=request.user,
                status=OrderItem.FulfillmentStatus.READY_FOR_PICKUP
            )

            # If found, update the status
            item.status = OrderItem.FulfillmentStatus.DELIVERED
            item.save()

            return JsonResponse({'success': True, 'message': f"Pickup confirmed for '{item.meal.name}'!"})

        except OrderItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid or incorrect barcode scanned.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'An unexpected error occurred.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)


def remove_from_cart(request, cart_item_id):
    cart = request.session.get('cart', [])

    # Find the item with the matching cart_item_id and remove it
    updated_cart = [item for item in cart if item['cart_item_id'] != cart_item_id]

    request.session['cart'] = updated_cart
    return redirect('view_cart')
