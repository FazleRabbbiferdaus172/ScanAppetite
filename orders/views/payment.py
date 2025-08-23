from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render

from orders.models import Order, OrderItem, Meal, Invoice


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

            OrderItem.objects.create(
                order=order,
                meal=meal,
                quantity=1,  # Quantity is always 1 now
                pickup_date=pickup_date_str,
                pickup_time=pickup_time,
                price=meal.price,
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

    customer_profile = getattr(request.user, 'profile', None)
    # if not customer_profile or not customer_profile.bank_account_number:
    #     messages.error(request, "Payment failed. Please add your bank details to your profile before proceeding.")
    #     return redirect('customer_profile')

    if hasattr(order, 'invoice'):
        order.invoice.status = Invoice.InvoiceStatus.PAID
        order.invoice.save()

    order.status = Order.OrderStatus.CONFIRMED
    order.is_paid = True
    order.save()

    return redirect('order_confirmation')
