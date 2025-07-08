from django.shortcuts import render, redirect
from django.views.generic import ListView
from .models import Meal
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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
    

