from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates default users for testing and development'

    def handle(self, *args, **options):
        users = [
            # Admin User
            {
                'email': 'admin@irony.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'phone_number': '+911234567890',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True
            },
            # Press/Staff User
            {
                'email': 'press@irony.com',
                'password': 'press123',
                'first_name': 'Press',
                'last_name': 'Staff',
                'phone_number': '+911234567891',
                'role': 'PRESS',
                'is_staff': True
            },
            # Delivery User
            {
                'email': 'delivery@irony.com',
                'password': 'delivery123',
                'first_name': 'Delivery',
                'last_name': 'Partner',
                'phone_number': '+911234567892',
                'role': 'DELIVERY'
            },
            # Customer User 1
            {
                'email': 'customer1@example.com',
                'password': 'customer123',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '+911234567893',
                'role': 'CUSTOMER'
            },
            # Customer User 2
            {
                'email': 'customer2@example.com',
                'password': 'customer123',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone_number': '+911234567894',
                'role': 'CUSTOMER'
            },
            # Press/Staff User 2
            {
                'email': 'press2@irony.com',
                'password': 'press123',
                'first_name': 'Michael',
                'last_name': 'Johnson',
                'phone_number': '+911234567895',
                'role': 'PRESS',
                'is_staff': True
            },
            # Delivery User 2
            {
                'email': 'delivery2@irony.com',
                'password': 'delivery123',
                'first_name': 'David',
                'last_name': 'Williams',
                'phone_number': '+911234567896',
                'role': 'DELIVERY'
            },
            # Admin User 2 (for testing)
            {
                'email': 'admin2@irony.com',
                'password': 'admin123',
                'first_name': 'Sarah',
                'last_name': 'Admin',
                'phone_number': '+911234567897',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True
            },
        ]

        created_count = 0
        for user_data in users:
            try:
                # Remove is_staff and is_superuser from user creation if they're not provided
                is_staff = user_data.pop('is_staff', False)
                is_superuser = user_data.pop('is_superuser', False)
                
                user, created = User.objects.get_or_create(
                    email=user_data['email'],
                    defaults=user_data
                )
                
                if created:
                    user.set_password(user_data['password'])
                    user.is_staff = is_staff
                    user.is_superuser = is_superuser
                    user.save()
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created {user.role.lower()} user: {user.email}'))
                else:
                    self.stdout.write(self.style.WARNING(f'User already exists: {user.email}'))
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Error creating user {user_data["email"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} users'))
