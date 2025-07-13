from django.urls import path
from .views import (
    homepage_view,
    VendorDashboardView,
    MealCreateView,
    MealUpdateView,
    MealDeleteView,
    add_to_cart,
    view_cart,
    checkout,
    invoice_detail_view,
    process_payment_view,
    update_order_item_status_view,
    order_confirmation_view,
    order_history_view,
    view_item_barcode,
    confirm_pickup_view,
    VendorOrderHistoryView,
    printable_barcode_view
)

urlpatterns = [
    path('', homepage_view, name='homepage'),
    path('add-to-cart/<int:meal_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('checkout/', checkout, name='checkout'),
    path('invoice/<int:order_id>/', invoice_detail_view, name='invoice_detail'),
    path('invoice/<int:order_id>/pay/', process_payment_view, name='process_payment'),
    path('order/confirmation/', order_confirmation_view, name='order_confirmation'),
    path('order-history/', order_history_view, name='order_history'),
    path('order-item/<int:item_id>/barcode/', view_item_barcode, name='view_item_barcode'),
    path('order-item/<int:item_id>/confirm-pickup/', confirm_pickup_view, name='confirm_pickup'),

    # Vendor views
    path('dashboard/', VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('dashboard/meal/add/', MealCreateView.as_view(), name='meal_add'),
    path('dashboard/meal/<int:pk>/edit/', MealUpdateView.as_view(), name='meal_edit'),
    path('dashboard/meal/<int:pk>/delete/', MealDeleteView.as_view(), name='meal_delete'),
    path('order-item/<int:item_id>/update-status/', update_order_item_status_view, name='update_order_item_status'),
    path('dashboard/history/', VendorOrderHistoryView.as_view(), name='vendor_order_history'),
    path('order-item/<int:item_id>/print/', printable_barcode_view, name='printable_barcode')
]