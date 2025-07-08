from django.urls import path
from .views import (
    homepage_view,
    VendorDashboardView,
    MealCreateView,
    MealUpdateView,
    MealDeleteView,
)

urlpatterns = [
    path('', homepage_view, name='homepage'),

    # Vendor views
    path('dashboard/', VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('dashboard/meal/add/', MealCreateView.as_view(), name='meal_add'),
    path('dashboard/meal/<int:pk>/edit/', MealUpdateView.as_view(), name='meal_edit'),
    path('dashboard/meal/<int:pk>/delete/', MealDeleteView.as_view(), name='meal_delete'),
]