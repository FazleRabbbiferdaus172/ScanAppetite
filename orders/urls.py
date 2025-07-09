from django.urls import path
from .views import (
    homepage_view,
    VendorDashboardView,
    MealCreateView,
    MealUpdateView,
    MealDeleteView,
    add_to_cart,
    view_cart,
    checkout
)

urlpatterns = [
    path('', homepage_view, name='homepage'),
    path('add-to-cart/<int:meal_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('checkout/', checkout, name='checkout'),

    # Vendor views
    path('dashboard/', VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('dashboard/meal/add/', MealCreateView.as_view(), name='meal_add'),
    path('dashboard/meal/<int:pk>/edit/', MealUpdateView.as_view(), name='meal_edit'),
    path('dashboard/meal/<int:pk>/delete/', MealDeleteView.as_view(), name='meal_delete'),
]