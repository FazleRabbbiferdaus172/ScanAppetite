from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from .forms import CustomerRegistrationForm, VendorRegistrationForm
from .models import CustomUser

class CustomerRegistrationView(CreateView):
    model = CustomUser
    form_class = CustomerRegistrationForm
    template_name = 'users/register_customer.html'
    success_url = reverse_lazy('login') # Redirect to login after success

    def form_valid(self, form):
        form.instance.user_type = CustomUser.UserType.CUSTOMER
        return super().form_valid(form)

class VendorRegistrationView(CreateView):
    model = CustomUser
    form_class = VendorRegistrationForm
    template_name = 'users/register_vendor.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.user_type = CustomUser.UserType.VENDOR
        return super().form_valid(form)
    

@login_required
def login_redirect_view(request):
    return redirect('homepage') 