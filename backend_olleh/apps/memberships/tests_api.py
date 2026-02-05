"""
API Tests for Membership Management System

Run with: python manage.py test apps.memberships.tests_api
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from users.models import User
from apps.memberships.models import Membership, UserMembership


class MembershipAPITestCase(TestCase):
    """Test cases for Membership API endpoints"""

    def setUp(self):
        """Set up test data"""
        # Create users
        self.client_user = User.objects.create_user(
            email="client@example.com",
            password="testpass123",
        )
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
        )

        # Create membership tiers (OLLEH: Basic 10k, Premium 20k RWF/year)
        self.basic = Membership.objects.create(
            name="Basic",
            price=10_000,
            max_order_price=100_000,
            description="Basic membership. Annual fee.",
            duration_days=365,
            is_available=True,
        )
        self.premium = Membership.objects.create(
            name="Premium",
            price=20_000,
            max_order_price=500_000,
            description="Premium membership. Annual fee.",
            duration_days=365,
            is_available=True,
        )

        # Initialize API client
        self.client_api = APIClient()

    def test_list_available_memberships(self):
        """Test that users can list available membership tiers"""
        self.client_api.force_authenticate(user=self.client_user)
        url = reverse("memberships:membership-list")
        response = self.client_api.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Basic")

    def test_create_membership_request(self):
        """Test that users can create a membership request"""
        self.client_api.force_authenticate(user=self.client_user)
        url = reverse("memberships:user-membership-list")

        data = {
            "membership": self.basic.id,
            "payment_mode": "mobile_money",
            "payment_reference": "MTN123456789",
            "amount_paid": 10_000,
        }

        response = self.client_api.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserMembership.objects.count(), 1)

        membership = UserMembership.objects.first()
        self.assertEqual(membership.user, self.client_user)
        self.assertEqual(membership.status, UserMembership.STATUS_PENDING)

    def test_create_membership_request_wrong_amount(self):
        """Test that request fails if amount doesn't match price"""
        self.client_api.force_authenticate(user=self.client_user)
        url = reverse("memberships:user-membership-list")

        data = {
            "membership": self.basic.id,
            "payment_mode": "mobile_money",
            "payment_reference": "MTN123456789",
            "amount_paid": 30000,  # Wrong amount
        }

        response = self.client_api.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_payment_info(self):
        """Test that users can update payment info for pending requests"""
        # Create a pending membership
        membership = UserMembership.objects.create(
            user=self.client_user,
            membership=self.basic,
            payment_mode=UserMembership.PAYMENT_MOBILE_MONEY,
            payment_reference="MTN111111111",
            amount_paid=self.basic.price,
            status=UserMembership.STATUS_PENDING,
        )

        self.client_api.force_authenticate(user=self.client_user)
        url = reverse(
            "memberships:user-membership-detail", kwargs={"pk": membership.id}
        )

        data = {
            "payment_reference": "MTN999999999",
        }

        response = self.client_api.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        membership.refresh_from_db()
        self.assertEqual(membership.payment_reference, "MTN999999999")

    def test_get_active_membership(self):
        """Test getting active membership"""
        # Create an active membership
        membership = UserMembership.objects.create(
            user=self.client_user,
            membership=self.basic,
            payment_mode=UserMembership.PAYMENT_MOBILE_MONEY,
            payment_reference="MTN123456789",
            amount_paid=self.basic.price,
            status=UserMembership.STATUS_PENDING,
        )
        membership.activate(self.admin_user)

        self.client_api.force_authenticate(user=self.client_user)
        url = reverse("memberships:user-membership-active")
        response = self.client_api.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], membership.id)
        self.assertEqual(response.data["status"], UserMembership.STATUS_ACTIVE)

    def test_cancel_membership_request(self):
        """Test canceling a membership request"""
        membership = UserMembership.objects.create(
            user=self.client_user,
            membership=self.basic,
            payment_mode=UserMembership.PAYMENT_MOBILE_MONEY,
            payment_reference="MTN123456789",
            amount_paid=self.basic.price,
            status=UserMembership.STATUS_PENDING,
        )

        self.client_api.force_authenticate(user=self.client_user)
        url = reverse(
            "memberships:user-membership-detail", kwargs={"pk": membership.id}
        )
        response = self.client_api.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        membership.refresh_from_db()
        self.assertEqual(membership.status, UserMembership.STATUS_CANCELED)

    def test_users_can_only_see_own_memberships(self):
        """Test that users can only see their own memberships"""
        # Create another user with a membership
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
        )
        UserMembership.objects.create(
            user=other_user,
            membership=self.basic,
            payment_mode=UserMembership.PAYMENT_MOBILE_MONEY,
            payment_reference="MTN123456789",
            amount_paid=self.basic.price,
            status=UserMembership.STATUS_PENDING,
        )

        # Client user should not see other user's membership
        self.client_api.force_authenticate(user=self.client_user)
        url = reverse("memberships:user-membership-list")
        response = self.client_api.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access endpoints"""
        url = reverse("memberships:membership-list")
        response = self.client_api.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserMembershipModelTestCase(TestCase):
    """Test cases for UserMembership model logic"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
        )
        self.membership = Membership.objects.create(
            name="Test Tier",
            price=10_000,
            max_order_price=100_000,
            description="Test tier (annual)",
            duration_days=365,
            is_available=True,
        )

    def test_mark_as_paid(self):
        """Test marking membership as paid"""
        user_membership = UserMembership.objects.create(
            user=self.user,
            membership=self.membership,
            payment_mode=UserMembership.PAYMENT_MOBILE_MONEY,
            payment_reference="MTN123456789",
            amount_paid=self.membership.price,
            status=UserMembership.STATUS_PENDING,
        )

        user_membership.mark_as_paid(self.admin)
        self.assertEqual(user_membership.status, UserMembership.STATUS_PAID)
        self.assertEqual(user_membership.payment_confirmed_by, self.admin)
        self.assertIsNotNone(user_membership.payment_confirmed_at)

    def test_activate_membership(self):
        """Test activating a membership"""
        user_membership = UserMembership.objects.create(
            user=self.user,
            membership=self.membership,
            payment_mode=UserMembership.PAYMENT_MOBILE_MONEY,
            payment_reference="MTN123456789",
            amount_paid=self.membership.price,
            status=UserMembership.STATUS_PENDING,
        )

        user_membership.activate(self.admin)
        self.assertEqual(user_membership.status, UserMembership.STATUS_ACTIVE)
        self.assertIsNotNone(user_membership.start_date)
        self.assertIsNotNone(user_membership.end_date)
        self.assertTrue(user_membership.is_active)

    def test_cancel_membership(self):
        """Test canceling a membership"""
        user_membership = UserMembership.objects.create(
            user=self.user,
            membership=self.membership,
            payment_mode=UserMembership.PAYMENT_MOBILE_MONEY,
            payment_reference="MTN123456789",
            amount_paid=self.membership.price,
            status=UserMembership.STATUS_PENDING,
        )

        user_membership.cancel()
        self.assertEqual(user_membership.status, UserMembership.STATUS_CANCELED)
        self.assertIsNotNone(user_membership.end_date)

    def test_only_one_active_membership_per_user(self):
        """Test that only one active membership is allowed per user"""
        # Create first active membership
        first_membership = UserMembership.objects.create(
            user=self.user,
            membership=self.membership,
            payment_mode=UserMembership.PAYMENT_MOBILE_MONEY,
            payment_reference="MTN111111111",
            amount_paid=self.membership.price,
            status=UserMembership.STATUS_PENDING,
        )
        first_membership.activate(self.admin)

        # Create second membership
        second_membership = UserMembership.objects.create(
            user=self.user,
            membership=self.membership,
            payment_mode=UserMembership.PAYMENT_MOBILE_MONEY,
            payment_reference="MTN222222222",
            amount_paid=self.membership.price,
            status=UserMembership.STATUS_PENDING,
        )

        # Activate second membership
        second_membership.activate(self.admin)

        # First membership should be expired
        first_membership.refresh_from_db()
        self.assertEqual(first_membership.status, UserMembership.STATUS_EXPIRED)

        # Second membership should be active
        self.assertEqual(second_membership.status, UserMembership.STATUS_ACTIVE)
