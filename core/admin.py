from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Sum, Count
from users.models import CustomUser, Profile
from orders.models import Order, Invoice

class CustomAdminSite(AdminSite):
    site_header = 'ScanAppetite Admin'
    site_title = 'ScanAppetite Admin Portal'
    index_title = 'Welcome to the ScanAppetite Admin Dashboard'

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Key Statistics
        extra_context['total_revenue'] = Invoice.objects.filter(status=Invoice.InvoiceStatus.PAID).aggregate(total=Sum('total_amount'))['total'] or 0
        extra_context['total_orders'] = Order.objects.count()
        extra_context['customer_count'] = CustomUser.objects.filter(user_type='CUSTOMER').count()
        extra_context['vendor_count'] = CustomUser.objects.filter(user_type='VENDOR').count()

        # Vendors Pending Approval
        extra_context['pending_vendors'] = CustomUser.objects.filter(user_type='VENDOR', profile__is_approved=False).order_by('-date_joined')

        # Recent Orders
        extra_context['recent_orders'] = Order.objects.order_by('-created_at')[:5]

        return super().index(request, extra_context)

custom_admin_site = CustomAdminSite(name='custom_admin')

# Register your models here.
