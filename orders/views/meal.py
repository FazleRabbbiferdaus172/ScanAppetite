from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from orders.forms import MealForm
from orders.models import Meal
from users.mixins import VendorRequiredMixin

class MealListView(ListView, LoginRequiredMixin, VendorRequiredMixin):
    model = Meal
    template_name = 'orders/meal_list.html'
    context_object_name = 'meals'

class MealCreateView(LoginRequiredMixin, VendorRequiredMixin, CreateView):
    model = Meal
    form_class = MealForm
    template_name = 'orders/meal_form.html'
    success_url = reverse_lazy('vendor_dashboard')

    def form_valid(self, form):
        # Automatically set the logged-in user as the vendor
        form.instance.vendor = self.request.user
        return super().form_valid(form)

class MealUpdateView(LoginRequiredMixin, VendorRequiredMixin, UpdateView):
    model = Meal
    form_class = MealForm
    template_name = 'orders/meal_form.html'
    success_url = reverse_lazy('vendor_dashboard')

    def get_queryset(self):
        return Meal.objects.filter(vendor=self.request.user)


class MealDeleteView(LoginRequiredMixin, VendorRequiredMixin, DeleteView):
    model = Meal
    template_name = 'orders/meal_confirm_delete.html'
    success_url = reverse_lazy('vendor_dashboard')

    def get_queryset(self):
        return Meal.objects.filter(vendor=self.request.user)

