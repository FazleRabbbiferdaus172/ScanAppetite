from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportIndexView.as_view(), name='index'),
    # path('admin/', views.AdminReportView.as_view(), name='admin_report'),
    path('vendor/', views.VendorReportView.as_view(), name='vendor_report'),
]