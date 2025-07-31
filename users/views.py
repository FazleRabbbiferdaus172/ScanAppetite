from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.decorators import login_required

from orders.models import Meal
from .forms import CustomerRegistrationForm, VendorRegistrationForm, StoreProfileForm, CustomerProfileForm, \
    VendorProfileForm
from .models import CustomUser, Profile

class CustomerRegistrationView(CreateView):
    model = CustomUser
    form_class = CustomerRegistrationForm
    template_name = 'users/register_customer.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.user_type = CustomUser.UserType.CUSTOMER
        user.save()
        Profile.objects.create(user=user)
        login(self.request, user)
        return redirect('homepage')


class VendorRegistrationView(CreateView):
    def get(self, request):
        user_form = VendorRegistrationForm()
        profile_form = VendorProfileForm()
        return render(request, 'users/register_vendor.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })

    def post(self, request):
        user_form = VendorRegistrationForm(request.POST)
        profile_form = VendorProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = CustomUser.UserType.VENDOR
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
        else:
            # If forms are invalid, re-render the page with errors
            return render(request, 'users/register_vendor.html', {
                'user_form': user_form,
                'profile_form': profile_form
            })


@login_required
def login_redirect_view(request):
    return redirect('homepage')


class CustomerProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = CustomerProfileForm
    template_name = 'users/customer_profile.html'
    success_url = reverse_lazy('homepage')

    def get_object(self):
        return self.request.user.profile


class StoreProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = StoreProfileForm
    template_name = 'users/store_profile.html'
    success_url = reverse_lazy('store_profile')

    def get_object(self):
        # Tell the view to edit the profile of the currently logged-in user
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        # Add the vendor's meal list to the page's context
        context = super().get_context_data(**kwargs)
        context['meals'] = Meal.objects.filter(vendor=self.request.user)
        return context
