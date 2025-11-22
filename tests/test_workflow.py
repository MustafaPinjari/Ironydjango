from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from orders.models import Order
from services.models import Service

class OrderWorkflowTest(TestCase):
    def setUp(self):
        # Create users
        self.customer = User.objects.create_user(email='customer@example.com', password='password', role=User.Role.CUSTOMER)
        self.press = User.objects.create_user(email='press@example.com', password='password', role=User.Role.PRESS)
        self.delivery = User.objects.create_user(email='delivery@example.com', password='password', role=User.Role.DELIVERY)
        self.admin = User.objects.create_superuser(email='admin@example.com', password='password')
        
        # Create service
        self.service = Service.objects.create(name='Wash & Fold', base_price=10.00)
        
        # Create order
        self.order = Order.objects.create(
            customer=self.customer,
            status=Order.Status.CONFIRMED,
            total_amount=20.00
        )
        
        self.client = Client()

    def test_full_workflow(self):
        print("\nTesting Order Workflow...")
        
        # 1. Press accepts order -> SCHEDULED_FOR_PICKUP
        self.client.force_login(self.press)
        response = self.client.post(reverse('dashboard:update_order_status', args=[self.order.pk]), {
            'status': 'scheduled_for_pickup'
        })
        self.order.refresh_from_db()
        print(f"1. Press Accept: {self.order.status}")
        self.assertEqual(self.order.status, Order.Status.SCHEDULED_FOR_PICKUP)
        
        # 2. Delivery accepts pickup -> OUT_FOR_PICKUP
        self.client.force_login(self.delivery)
        response = self.client.post(reverse('dashboard:update_order_status', args=[self.order.pk]), {
            'status': 'out_for_pickup'
        })
        self.order.refresh_from_db()
        print(f"2. Delivery Accept Pickup: {self.order.status}")
        self.assertEqual(self.order.status, Order.Status.OUT_FOR_PICKUP)
        
        # 3. Delivery confirms pickup -> PICKED_UP
        response = self.client.post(reverse('dashboard:update_order_status', args=[self.order.pk]), {
            'status': 'picked_up'
        })
        self.order.refresh_from_db()
        print(f"3. Delivery Confirm Pickup: {self.order.status}")
        self.assertEqual(self.order.status, Order.Status.PICKED_UP)
        
        # 4. Press starts processing -> PROCESSING
        self.client.force_login(self.press)
        response = self.client.post(reverse('dashboard:update_order_status', args=[self.order.pk]), {
            'status': 'processing'
        })
        self.order.refresh_from_db()
        print(f"4. Press Start Processing: {self.order.status}")
        self.assertEqual(self.order.status, Order.Status.PROCESSING)
        
        # 5. Press marks ready -> READY
        response = self.client.post(reverse('dashboard:update_order_status', args=[self.order.pk]), {
            'status': 'ready'
        })
        self.order.refresh_from_db()
        print(f"5. Press Mark Ready: {self.order.status}")
        self.assertEqual(self.order.status, Order.Status.READY)
        
        # 6. Delivery accepts delivery -> OUT_FOR_DELIVERY
        self.client.force_login(self.delivery)
        response = self.client.post(reverse('dashboard:update_order_status', args=[self.order.pk]), {
            'status': 'out_for_delivery'
        })
        self.order.refresh_from_db()
        print(f"6. Delivery Accept Delivery: {self.order.status}")
        self.assertEqual(self.order.status, Order.Status.OUT_FOR_DELIVERY)
        
        # 7. Delivery confirms delivery -> COMPLETED
        response = self.client.post(reverse('dashboard:update_order_status', args=[self.order.pk]), {
            'status': 'completed'
        })
        self.order.refresh_from_db()
        print(f"7. Delivery Confirm Delivery: {self.order.status}")
        self.assertEqual(self.order.status, Order.Status.COMPLETED)
        
        print("Workflow test passed!")
