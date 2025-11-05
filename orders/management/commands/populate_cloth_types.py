from django.core.management.base import BaseCommand
from orders.models import ClothType


class Command(BaseCommand):
    help = 'Populate the database with default cloth types'

    def handle(self, *args, **kwargs):
        cloth_types = [
            {'name': 'Shirt', 'price_per_unit': 30.00, 'description': 'Regular shirt'},
            {'name': 'Pant', 'price_per_unit': 40.00, 'description': 'Regular pant'},
            {'name': 'Jeans', 'price_per_unit': 50.00, 'description': 'Denim jeans'},
            {'name': 'T-Shirt', 'price_per_unit': 20.00, 'description': 'Casual t-shirt'},
            {'name': 'Suit', 'price_per_unit': 100.00, 'description': 'Formal suit'},
            {'name': 'Dress', 'price_per_unit': 60.00, 'description': 'Dress'},
            {'name': 'Skirt', 'price_per_unit': 35.00, 'description': 'Skirt'},
            {'name': 'Blouse', 'price_per_unit': 25.00, 'description': 'Blouse'},
            {'name': 'Sweater', 'price_per_unit': 45.00, 'description': 'Sweater'},
            {'name': 'Jacket', 'price_per_unit': 70.00, 'description': 'Jacket'},
        ]

        created_count = 0
        updated_count = 0

        for cloth_data in cloth_types:
            cloth_type, created = ClothType.objects.get_or_create(
                name=cloth_data['name'],
                defaults={
                    'price_per_unit': cloth_data['price_per_unit'],
                    'description': cloth_data['description'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created cloth type: {cloth_type.name} - ${cloth_type.price_per_unit}')
                )
            else:
                # Update existing cloth type
                cloth_type.price_per_unit = cloth_data['price_per_unit']
                cloth_type.description = cloth_data['description']
                cloth_type.is_active = True
                cloth_type.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated cloth type: {cloth_type.name} - ${cloth_type.price_per_unit}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSummary: {created_count} created, {updated_count} updated')
        )
