from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView

# Create your views here.

class LandingPageView(TemplateView):
    template_name = 'core/landing_page.html'

    def dispatch(self, request, *args, **kwargs):
        # If user is already logged in, redirect them to the homepage
        if request.user.is_authenticated:
            return redirect('homepage')
        return super().dispatch(request, *args, **kwargs)

class HomepageView(ListView):
    model = YourModelHere  # Replace with your actual model
    template_name = 'core/homepage.html'
    context_object_name = 'items'  # Replace with your actual context object name

    def get_queryset(self):
        # Customize your queryset here
        return super().get_queryset().filter(is_active=True)  # Example filter
