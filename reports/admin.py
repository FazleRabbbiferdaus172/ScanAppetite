from django.contrib import admin
from django.urls import path
from .views import AdminReportView
# Register your models here.


class CustomOrderAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reports/', AdminReportView.as_view(), name='admin_report')
        ]
        return custom_urls + urls