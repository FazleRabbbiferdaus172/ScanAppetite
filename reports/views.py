from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from datetime import datetime, timedelta

from orders.models import Invoice, OrderItem
from users.models import CustomUser
from users.mixins import AdminRequiredMixin, VendorRequiredMixin
from django.db.models import Sum, Count, F

class PDFReportMixin:
    """A mixin to handle PDF generation for any report view."""
    def render_to_pdf(self, template_name, context):
        html_string = render_to_string(template_name, context)
        html = HTML(string=html_string, base_url=self.request.build_absolute_uri())
        pdf = html.write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        return response

    def get(self, request, *args, **kwargs):
        if request.GET.get('format') == 'pdf':
            context = self.get_context_data(**kwargs)
            return self.render_to_pdf(self.template_name, context)
        return super().get(request, *args, **kwargs)

class ReportIndexView(LoginRequiredMixin, TemplateView):
    """Directs users to the correct report based on their role."""
    template_name = 'reports/index.html'


# Todo: downloaded pdf reports should have different kind of structure as current one just dumps the whole html to a pfd
class AdminReportView(LoginRequiredMixin, AdminRequiredMixin, PDFReportMixin, TemplateView):
    template_name = 'reports/admin_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Date filtering
        date_from_str = self.request.GET.get('date_from', '')
        date_to_str = self.request.GET.get('date_to', '')
        
        invoices = Invoice.objects.filter(status=Invoice.InvoiceStatus.PAID)
        if date_from_str and date_to_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d') + timedelta(days=1)
            invoices = invoices.filter(issued_at__range=(date_from, date_to))
        
        context['total_revenue'] = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        context['total_orders'] = invoices.count()
        context['date_from'] = date_from_str
        context['date_to'] = date_to_str
        return context

class VendorReportView(LoginRequiredMixin, VendorRequiredMixin, PDFReportMixin, TemplateView):
    template_name = 'reports/vendor_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.request.user

        # Date filtering
        date_from_str = self.request.GET.get('date_from', '')
        date_to_str = self.request.GET.get('date_to', '')

        items = OrderItem.objects.filter(meal__vendor=vendor, status=OrderItem.FulfillmentStatus.DELIVERED)
        if date_from_str and date_to_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d') + timedelta(days=1)
            items = items.filter(order__created_at__range=(date_from, date_to))

        context['total_revenue'] = items.annotate(
            item_total=F('quantity') * F('meal__price')
        ).aggregate(total=Sum('item_total'))['total'] or 0
        context['total_meals_sold'] = items.aggregate(total=Sum('quantity'))['total'] or 0
        context['date_from'] = date_from_str
        context['date_to'] = date_to_str
        return context
