from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test users with different roles for development and testing'

    def handle(self, *args, **options):
        users_data = [
            # Super Admins
            {
                'email': 'admin@irony.com',
                'password': 'admin123',
                'phone_number': '+911234567890',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True
            },
            {
                'email': 'admin2@irony.com',
                'password': 'admin123',
                'phone_number': '+911234567897',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True
            },
            # Press/Staff Users
            {
                'email': 'press@irony.com',
                'password': 'press123',
                'phone_number': '+911234567891',
                'role': 'PRESS',
                'is_staff': True,
            },
            {
                'email': 'press2@irony.com',
                'password': 'press123',
                'phone_number': '+911234567895',
                'role': 'PRESS',
                'is_staff': True,
            },
            # Delivery Partners
            {
                'email': 'delivery@irony.com',
                'password': 'delivery123',
                'phone_number': '+911234567892',
                'role': 'DELIVERY',
            },
            {
                'email': 'delivery2@irony.com',
                'password': 'delivery123',
                'phone_number': '+911234567896',
                'role': 'DELIVERY',
            },
            # Customers
            {
                'email': 'customer1@example.com',
                'password': 'customer123',
                'phone_number': '+911234567893',
                'role': 'CUSTOMER',
            },
            {
                'email': 'customer2@example.com',
                'password': 'customer123',
                'phone_number': '+911234567894',
                'role': 'CUSTOMER',
            },
        ]

        created_count = 0
        with transaction.atomic():
            for user_data in users_data:
                email = user_data.pop('email')
                password = user_data.pop('password')
                
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults=user_data
                )
                
                if created:
                    user.set_password(password)
                    user.save()
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created user: {email} ({user_data["role"]})'))
                else:
                    self.stdout.write(self.style.WARNING(f'User already exists: {email}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} test users'))
