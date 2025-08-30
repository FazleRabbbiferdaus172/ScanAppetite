from django.contrib import admin
from .models import Meal, Order, OrderItem, Invoice
from core.admin import custom_admin_site

# Register your models here.
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price')
    list_filter = ['vendor']
    search_fields = ('name', 'vendor__username')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'created_at', 'commission')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('order', 'total_amount', 'status', 'commission')
    list_filter = ('status',)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'meal', 'quantity', 'price','sub_total', 'status')
    list_filter = ('status',)

# Register with the custom admin site
custom_admin_site.register(Meal, MealAdmin)
custom_admin_site.register(Order, OrderAdmin)
custom_admin_site.register(Invoice, InvoiceAdmin)
custom_admin_site.register(OrderItem, OrderItemAdmin)
