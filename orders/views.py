from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from .models import Meal, Order, OrderItem
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from .models import Meal
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
    context_object_name = 'meals' # The name of the variable in the template



class VendorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'VENDOR'



# View for the Vendor's Dashboard (lists their own meals)
class VendorDashboardView(LoginRequiredMixin, VendorRequiredMixin, ListView):
    model = Meal
    template_name = 'orders/vendor_dashboard.html'
    context_object_name = 'meals'

    def get_queryset(self):
        # Filter meals to show only those created by the current logged-in vendor
        return Meal.objects.filter(vendor=self.request.user)



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
    cart = request.session.get('cart', {})
    
    # Add the meal to the cart or increment its quantity
    meal_id_str = str(meal_id)
    quantity = cart.get(meal_id_str, 0) + 1
    cart[meal_id_str] = quantity
    
    # Save the updated cart back to the session
    request.session['cart'] = cart
    
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

    # Create the main order
    order = Order.objects.create(customer=request.user)
    
    # Create order items from the cart
    for meal_id, quantity in cart.items():
        meal = get_object_or_404(Meal, id=int(meal_id))
        OrderItem.objects.create(order=order, meal=meal, quantity=quantity)
    
    # Clear the cart from the session
    request.session['cart'] = {}
    
    return redirect('order_confirmation') # Redirect to your existing success page
    

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
        
    return render(request, 'orders/cart_details.html', {
        'cart_items': cart_items, 
        'total_price': total_price
    })

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('homepage')

    # Create the main order for the logged-in user
    order = Order.objects.create(customer=request.user)
    
    # Create an OrderItem for each item in the cart
    for meal_id, quantity in cart.items():
        meal = get_object_or_404(Meal, id=int(meal_id))
        OrderItem.objects.create(order=order, meal=meal, quantity=quantity)
    
    # Clear the cart from the session
    request.session['cart'] = {}
    
    return redirect('order_confirmation')

