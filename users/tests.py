from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import time
import pytz
from freezegun import freeze_time

from .models import CustomUser, Profile

class ProfileModelTests(TestCase):
    """Tests for the Profile model and its properties."""

    def setUp(self):
        """Set up a test user and profile for all tests in this class."""
        self.user = CustomUser.objects.create_user(
            username='testvendor', 
            password='password123',
            user_type='VENDOR'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            timezone='America/New_York'  # Use a non-UTC timezone for robust testing
        )

    def test_is_open_property_normal_hours(self):
        """Test the is_open property for a store with same-day hours."""
        self.profile.store_open_time = time(9, 0)   # 9 AM
        self.profile.store_close_time = time(17, 0) # 5 PM
        self.profile.save()

        # Check when store should be open (e.g., 1 PM New York time, which is 17:00 UTC on this date)
        with freeze_time("2025-08-07 17:00:00", tz_offset=pytz.utc):
            self.assertTrue(self.profile.is_open)

        # Check when store should be closed (e.g., 8 PM New York time, which is 00:00 UTC the next day)
        with freeze_time("2025-08-08 00:00:00", tz_offset=pytz.utc):
            self.assertFalse(self.profile.is_open)

    def test_is_open_property_overnight_hours(self):
        """Test the is_open property for a store with overnight hours."""
        self.profile.store_open_time = time(22, 0) # 10 PM
        self.profile.store_close_time = time(5, 0)  # 5 AM
        self.profile.save()

        # Check when store should be open (e.g., 11 PM New York time -> 03:00 UTC next day)
        with freeze_time("2025-08-08 03:00:00", tz_offset=pytz.utc):
            self.assertTrue(self.profile.is_open)

        # Check when store should be open (e.g., 2 AM New York time -> 06:00 UTC same day)
        with freeze_time("2025-08-07 06:00:00", tz_offset=pytz.utc):
            self.assertTrue(self.profile.is_open)

        # Check when store should be closed (e.g., 12 PM New York time -> 16:00 UTC same day)
        with freeze_time("2025-08-07 16:00:00", tz_offset=pytz.utc):
            self.assertFalse(self.profile.is_open)

    def test_is_open_no_times_set(self):
        """Test that is_open is False if opening/closing times are not set."""
        self.profile.store_open_time = None
        self.profile.store_close_time = None
        self.profile.save()
        self.assertFalse(self.profile.is_open)


class CustomerProfileViewTests(TestCase):
    """Tests for the customer profile view."""

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testcustomer', 
            password='password123',
            user_type='CUSTOMER'
        )
        self.profile_url = reverse('customer_profile')

    def test_profile_view_redirects_if_not_logged_in(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_profile_view_accessible_if_logged_in(self):
        """Test that an authenticated customer can access their profile page."""
        self.client.login(username='testcustomer', password='password123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/customer_profile.html')

    def test_profile_view_displays_user_info(self):
        """Test that the profile page displays the correct user's information."""
        self.client.login(username='testcustomer', password='password123')
        response = self.client.get(self.profile_url)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.email)