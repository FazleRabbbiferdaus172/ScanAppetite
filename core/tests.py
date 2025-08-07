from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from users.models import CustomUser, Profile
from orders.models import Order, Invoice

class CustomAdminTests(TestCase):
    """Tests for the custom admin site and its actions."""

    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_superuser('admin', 'admin@test.com', 'password123')
        self.client.login(username='admin', password='password123')

        # Create users for testing dashboard stats
        self.vendor1 = CustomUser.objects.create_user('vendor1', 'v1@test.com', 'pw', user_type='VENDOR')
        self.vendor2 = CustomUser.objects.create_user('vendor2', 'v2@test.com', 'pw', user_type='VENDOR')
        self.customer = CustomUser.objects.create_user('customer', 'c@test.com', 'pw', user_type='CUSTOMER')

        # Make one vendor approved, one pending
        self.vendor1.profile.is_approved = True
        self.vendor1.profile.save()
        # vendor2 is pending by default

    def test_admin_dashboard_context(self):
        """Test that the admin dashboard view has the correct context data."""
        # Create some data to test statistics
        order = Order.objects.create(customer=self.customer)
        Invoice.objects.create(order=order, total_amount=100.00, status=Invoice.InvoiceStatus.PAID)
        
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        
        # Check statistics
        self.assertEqual(response.context['total_revenue'], 100.00)
        self.assertEqual(response.context['total_orders'], 1)
        self.assertEqual(response.context['customer_count'], 1)
        self.assertEqual(response.context['vendor_count'], 2)
        
        # Check pending vendors list
        self.assertEqual(len(response.context['pending_vendors']), 1)
        self.assertEqual(response.context['pending_vendors'][0], self.vendor2)

    def test_approve_vendors_admin_action(self):
        """Test the 'approve_vendors' action in the CustomUser admin."""
        self.assertFalse(self.vendor2.profile.is_approved) # Verify initial state

        changelist_url = reverse('admin:users_customuser_changelist')
        action_data = {
            'action': 'approve_vendors',
            '_selected_action': [str(self.vendor2.id)]
        }
        response = self.client.post(changelist_url, action_data)
        self.assertEqual(response.status_code, 302) # Action redirects back to the changelist

        self.vendor2.profile.refresh_from_db()
        self.assertTrue(self.vendor2.profile.is_approved) # Verify it was approved