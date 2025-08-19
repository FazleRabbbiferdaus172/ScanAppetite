import uuid
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from orders.models import Meal


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


def remove_from_cart(request, cart_item_id):
    cart = request.session.get('cart', [])

    # Find the item with the matching cart_item_id and remove it
    updated_cart = [item for item in cart if item['cart_item_id'] != cart_item_id]

    request.session['cart'] = updated_cart
    return redirect('view_cart')
