from django.core.management.base import BaseCommand
from services.models import Service, ServiceVariant, ServiceOption, ServiceOptionChoice
from decimal import Decimal

class Command(BaseCommand):
    help = 'Add more variants and options to services'

    def handle(self, *args, **options):
        # Add more variants to Dry Cleaning service (ID 2)
        dry_cleaning = Service.objects.get(pk=2)
        
        # Add more variants
        variants = [
            {
                'service': dry_cleaning,
                'name': 'Express (24h)',
                'description': 'Faster dry cleaning service',
                'price_adjustment': Decimal('10.00'),
                'is_default': False,
                'is_active': True
            },
            {
                'service': dry_cleaning,
                'name': 'Delicate Items',
                'description': 'Special handling for delicate fabrics',
                'price_adjustment': Decimal('15.00'),
                'is_default': False,
                'is_active': True
            },
            {
                'service': dry_cleaning,
                'name': 'Bulk (5+ items)',
                'description': 'Discount for 5 or more items',
                'price_adjustment': Decimal('-5.00'),
                'is_default': False,
                'is_active': True
            }
        ]
        
        for variant_data in variants:
            variant, created = ServiceVariant.objects.get_or_create(
                service=variant_data['service'],
                name=variant_data['name'],
                defaults=variant_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created variant: {variant.name}'))
        
        # Add options to Dry Cleaning service
        options = [
            {
                'name': 'Stain Removal',
                'description': 'Special treatment for tough stains',
                'option_type': 'checkbox',
                'price_adjustment': Decimal('5.00'),
                'is_required': False,
                'is_active': True,
                'display_order': 1,
                'service': dry_cleaning
            },
            {
                'name': 'Fabric Protection',
                'description': 'Add fabric protection treatment',
                'option_type': 'checkbox',
                'price_adjustment': Decimal('8.00'),
                'is_required': False,
                'is_active': True,
                'display_order': 2,
                'service': dry_cleaning
            },
            {
                'name': 'Hanger or Fold',
                'description': 'How would you like your items returned?',
                'option_type': 'select',
                'price_adjustment': Decimal('0.00'),
                'is_required': True,
                'is_active': True,
                'display_order': 3,
                'service': dry_cleaning
            }
        ]
        
        for option_data in options:
            option, created = ServiceOption.objects.get_or_create(
                service=option_data['service'],
                name=option_data['name'],
                defaults=option_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created option: {option.name}'))
                
                # Add choices for the 'Hanger or Fold' option
                if option.name == 'Hanger or Fold':
                    choices = [
                        {
                            'option': option,
                            'name': 'On Hangers',
                            'value': 'hangers',
                            'price_adjustment': Decimal('0.00'),
                            'is_default': True,
                            'display_order': 1
                        },
                        {
                            'option': option,
                            'name': 'Folded',
                            'value': 'folded',
                            'price_adjustment': Decimal('0.00'),
                            'is_default': False,
                            'display_order': 2
                        },
                        {
                            'option': option,
                            'name': 'On Hangers with Cover',
                            'value': 'hangers_with_cover',
                            'price_adjustment': Decimal('2.00'),
                            'is_default': False,
                            'display_order': 3
                        }
                    ]
                    
                    for choice_data in choices:
                        choice, created = ServiceOptionChoice.objects.get_or_create(
                            option=choice_data['option'],
                            value=choice_data['value'],
                            defaults=choice_data
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'  - Created choice: {choice.name}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully added more variants and options!'))
