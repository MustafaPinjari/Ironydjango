from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User

class DashboardRedirectionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(email='customer@example.com', password='password', role=User.Role.CUSTOMER)
        self.press = User.objects.create_user(email='press@example.com', password='password', role=User.Role.PRESS)
        self.delivery = User.objects.create_user(email='delivery@example.com', password='password', role=User.Role.DELIVERY)
        self.admin = User.objects.create_superuser(email='admin@example.com', password='password')

    def test_customer_redirection(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse('dashboard:home'))
        self.assertRedirects(response, reverse('dashboard:customer_dashboard'))

    def test_press_redirection(self):
        self.client.force_login(self.press)
        response = self.client.get(reverse('dashboard:home'))
        self.assertRedirects(response, reverse('dashboard:press_dashboard'))

    def test_delivery_redirection(self):
        self.client.force_login(self.delivery)
        response = self.client.get(reverse('dashboard:home'))
        self.assertRedirects(response, reverse('dashboard:delivery_dashboard'))

    def test_admin_redirection(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('dashboard:home'))
        self.assertRedirects(response, reverse('dashboard:admin_dashboard'))
