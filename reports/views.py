from weasyprint import HTML
from datetime import datetime, timedelta

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from django.contrib.staticfiles import finders
from django.contrib import admin

from core.admin import custom_admin_site
from orders.models import Invoice, OrderItem
from users.mixins import AdminRequiredMixin, VendorRequiredMixin
from django.db.models import Sum, F

from users.models import CustomUser


class PDFReportMixin:
    """
    A mixin that can be used to render a PDF report.
    """
    def render_to_pdf(self, template_src, context_dict, request):
        # Render the HTML string from the template
        html_string = render_to_string(template_src, context_dict, request=request)

        # Find the absolute path to the main CSS file
        # This is the crucial step for styling the PDF
        css_path = finders.find('css/custom-bootstrap.css')

        # Create a list of WeasyPrint CSS objects
        stylesheets = []
        if css_path:
            stylesheets.append(CSS(css_path))
        else:
            # Optional: handle case where CSS is not found
            print("Warning: custom-bootstrap.css not found for PDF rendering.")

        # Create a WeasyPrint HTML object
        # The base_url is important for resolving relative paths for images, etc.
        html = HTML(string=html_string, base_url=request.build_absolute_uri())

        # Generate the PDF
        pdf = html.write_pdf(stylesheets=stylesheets)

        # Create the HTTP response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="vendor-report.pdf"'
        return response

    def get(self, request, *args, **kwargs):
        if request.GET.get('format') == 'pdf':
            context = self.get_context_data(**kwargs)
            return self.render_to_pdf(self.template_name, context, request)
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
        vendor_id_str = self.request.GET.get('vendor_id')
        
        items = OrderItem.objects.filter(status=OrderItem.FulfillmentStatus.DELIVERED)
        if date_from_str and date_to_str and vendor_id_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d') + timedelta(days=1)
            vendor = CustomUser.objects.get(id=vendor_id_str)
            items = OrderItem.objects.filter(meal__vendor=vendor, status=OrderItem.FulfillmentStatus.DELIVERED, order__created_at__range=(date_from, date_to))
        
        total_revenue_agg = items.aggregate(total=Sum(F('quantity') * F('meal__price')))
        context['total_revenue'] = total_revenue_agg['total'] or 0
        context['total_meals_sold'] = items.aggregate(total=Sum('quantity'))['total'] or 0
        top_meals = items.values('meal__name').annotate(
            total_quantity_sold=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('meal__price'))
        ).order_by('-total_quantity_sold')
        context['order_items'] = items.select_related('order', 'meal') # For Detailed Sales table
        context['top_meals'] = top_meals

        # Pass data to the template context
        context['order_items'] = items.select_related('order', 'meal')
        context['date_from'] = date_from_str
        context['date_to'] = date_to_str
        context['all_vendors'] = CustomUser.objects.filter(user_type__in=[CustomUser.UserType.VENDOR])
        context['selected_vendor_id'] = int(vendor_id_str) if vendor_id_str else None
        context.update(custom_admin_site.each_context(self.request))
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

        # Calculate total revenue and meals sold using the meal's price
        total_revenue_agg = items.aggregate(total=Sum(F('quantity') * F('meal__price')))
        context['total_revenue'] = total_revenue_agg['total'] or 0
        context['total_meals_sold'] = items.aggregate(total=Sum('quantity'))['total'] or 0

        # Query for Top Selling Meals table using the meal's price
        top_meals = items.values('meal__name').annotate(
            total_quantity_sold=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('meal__price'))
        ).order_by('-total_quantity_sold')

        # Pass data to the template context
        context['order_items'] = items.select_related('order', 'meal') # For Detailed Sales table
        context['top_meals'] = top_meals # For Top Selling Meals table
        context['date_from'] = date_from_str
        context['date_to'] = date_to_str
        return context
