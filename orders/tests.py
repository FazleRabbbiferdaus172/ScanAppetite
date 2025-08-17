from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, time

from users.models import CustomUser, Profile
from .models import Meal, Order, OrderItem

# Todo: need more test cases before we start refactoring, maybe mix of TDD approach will be good if this is separated into multiple files
class OrderFlowTests(TestCase):
    """Tests the full customer order flow from homepage to checkout."""

    def setUp(self):
        self.client = Client()
        self.customer = CustomUser.objects.create_user('customer', 'c@test.com', 'pw123', user_type='CUSTOMER')
        
        # Approved vendor with bank details
        self.approved_vendor = CustomUser.objects.create_user('approved_vendor', 'v1@test.com', 'pw123', user_type='VENDOR')
        self.approved_vendor.profile.is_approved = True
        self.approved_vendor.profile.bank_account_number = '12345'
        self.approved_vendor.profile.save()
        self.approved_meal = Meal.objects.create(vendor=self.approved_vendor, name='Approved Pizza', price=10.00)

        # Unapproved vendor
        self.unapproved_vendor = CustomUser.objects.create_user('unapproved_vendor', 'v2@test.com', 'pw123', user_type='VENDOR')
        self.unapproved_meal = Meal.objects.create(vendor=self.unapproved_vendor, name='Pending Pizza', price=12.00)

    def test_homepage_filters_unapproved_vendors(self):
        """Homepage should only show meals from approved vendors with bank details."""
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.approved_meal.name)
        self.assertNotContains(response, self.unapproved_meal.name)

    def test_add_to_cart_and_checkout(self):
        """Test adding an item to the cart and completing the checkout process."""
        self.client.login(username='customer', password='pw123')

        # 1. Add to cart
        add_url = reverse('add_to_cart', args=[self.approved_meal.id])
        self.client.post(add_url)
        self.assertEqual(len(self.client.session['cart']), 1)
        self.assertEqual(self.client.session['cart'][0]['meal_id'], self.approved_meal.id)

        # 2. View cart and proceed to checkout
        cart_url = reverse('view_cart')
        response = self.client.get(cart_url)
        self.assertContains(response, self.approved_meal.name)

        # 3. Checkout
        checkout_url = reverse('checkout')
        cart_item_id = self.client.session['cart'][0]['cart_item_id']
        checkout_data = {
            f'pickup_date_{cart_item_id}': '2025-08-08',
            f'pickup_time_{cart_item_id}': '14:30',
        }
        response = self.client.post(checkout_url, checkout_data)
        
        # Verify order creation and redirection to invoice
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.customer, self.customer)
        self.assertRedirects(response, reverse('invoice_detail', args=[order.id]))
        self.assertEqual(self.client.session['cart'], []) # Cart should be empty


class VendorManagementTests(TestCase):
    """Tests for vendor-specific views like the dashboard and status updates."""

    def setUp(self):
        self.client = Client()
        self.vendor = CustomUser.objects.create_user('vendor', 'v@test.com', 'pw123', user_type='VENDOR')
        self.other_vendor = CustomUser.objects.create_user('othervendor', 'ov@test.com', 'pw123', user_type='VENDOR')
        self.customer = CustomUser.objects.create_user('customer', 'c@test.com', 'pw123', user_type='CUSTOMER')
        
        self.meal = Meal.objects.create(vendor=self.vendor, name='Test Meal', price=5.00)
        self.order = Order.objects.create(customer=self.customer, status=Order.OrderStatus.CONFIRMED)
        self.order_item = OrderItem.objects.create(order=self.order, meal=self.meal, quantity=1)

    def test_vendor_can_update_own_order_status(self):
        """A vendor should be able to update the status of their own order items."""
        self.client.login(username='vendor', password='pw123')
        update_url = reverse('update_item_status', args=[self.order_item.id, 'PROCESSING'])
        response = self.client.post(update_url)
        
        self.assertRedirects(response, reverse('vendor_dashboard'))
        self.order_item.refresh_from_db()
        self.assertEqual(self.order_item.status, 'PROCESSING')

    def test_vendor_cannot_update_other_vendors_order(self):
        """A vendor should not be able to update another vendor's order item."""
        self.client.login(username='othervendor', password='pw123')
        update_url = reverse('update_item_status', args=[self.order_item.id, 'PROCESSING'])
        response = self.client.post(update_url)
        self.assertEqual(response.status_code, 404) # Should not find the item