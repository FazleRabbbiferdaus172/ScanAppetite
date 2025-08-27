from collections import defaultdict

from django.shortcuts import redirect, render

from orders.models import Meal
from users.models import CustomUser

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView

# Create your views here.

class LandingPageView(TemplateView):
    template_name = 'orders/landing_page.html'

    def dispatch(self, request, *args, **kwargs):
        # If user is already logged in, redirect them to the homepage
        if request.user.is_authenticated:
            return redirect('homepage')
        return super().dispatch(request, *args, **kwargs)



def homepage_view(request):
    if request.user.is_authenticated and request.user.user_type == 'VENDOR':
        return redirect('vendor_dashboard')

    meals_query = Meal.objects.select_related('vendor__profile').filter(
        vendor__profile__is_approved=True,
        vendor__profile__bank_account_number__isnull=False,
    )

    vendors_dict = defaultdict(lambda: {'meals': [], 'profile': None, 'is_open': False})

    for meal in meals_query:
        vendor = meal.vendor
        profile = vendor.profile

        # Store vendor data if not already stored
        if vendor.id not in vendors_dict:
            vendors_dict[vendor.id]['profile'] = profile
            # The calculation is now done in the model property!
            vendors_dict[vendor.id]['is_open'] = profile.is_open

        # Add meal to the vendor's meal list
        vendors_dict[vendor.id]['meals'].append(meal)

    # Prepare the final context list
    vendors_with_meals = [
        {'vendor': CustomUser.objects.get(id=vid), 'data': vdata}
        for vid, vdata in vendors_dict.items()
    ]

    context = {'vendors_with_meals': vendors_with_meals}
    return render(request, 'orders/meal_list.html', context)