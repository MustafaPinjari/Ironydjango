import json
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates initial data for the application'

    def handle(self, *args, **options):
        # Create categories
        categories = [
            {
                "model": "services.servicecategory",
                "pk": 1,
                "fields": {
                    "name": "Laundry",
                    "slug": "laundry",
                    "description": "Regular laundry services including washing and folding",
                    "icon": "fas fa-tshirt",
                    "is_active": True,
                    "display_order": 1
                }
            },
            {
                "model": "services.servicecategory",
                "pk": 2,
                "fields": {
                    "name": "Dry Cleaning",
                    "slug": "dry-cleaning",
                    "description": "Professional dry cleaning services",
                    "icon": "fas fa-tshirt",
                    "is_active": True,
                    "display_order": 2
                }
            },
            {
                "model": "services.servicecategory",
                "pk": 3,
                "fields": {
                    "name": "Ironing",
                    "slug": "ironing",
                    "description": "Professional ironing and pressing services",
                    "icon": "fas fa-iron",
                    "is_active": True,
                    "display_order": 3
                }
            }
        ]

        # Create services
        services = [
            {
                "model": "services.service",
                "pk": 1,
                "fields": {
                    "name": "Wash & Fold",
                    "slug": "wash-fold",
                    "service_type": "wash_fold",
                    "category": 1,
                    "short_description": "Professional washing and folding service",
                    "description": "Our standard wash and fold service includes washing, drying, and folding your clothes with care.",
                    "instructions": "Please separate colors and whites. Check all pockets before submitting.",
                    "base_price": "15.00",
                    "is_taxable": True,
                    "min_processing_duration": 24,
                    "max_processing_duration": 48,
                    "duration_unit": "hours",
                    "is_active": True,
                    "is_featured": True,
                    "display_order": 1
                }
            },
            {
                "model": "services.service",
                "pk": 2,
                "fields": {
                    "name": "Dry Cleaning",
                    "slug": "dry-cleaning",
                    "service_type": "dry_clean",
                    "category": 2,
                    "short_description": "Professional dry cleaning for delicate items",
                    "description": "Expert dry cleaning service for your delicate and special care items.",
                    "instructions": "Please inform us of any stains or special requirements.",
                    "base_price": "25.00",
                    "is_taxable": True,
                    "min_processing_duration": 48,
                    "max_processing_duration": 72,
                    "duration_unit": "hours",
                    "is_active": True,
                    "is_featured": True,
                    "display_order": 2
                }
            },
            {
                "model": "services.service",
                "pk": 3,
                "fields": {
                    "name": "Ironing Service",
                    "slug": "ironing-service",
                    "service_type": "ironing",
                    "category": 3,
                    "short_description": "Professional ironing and pressing",
                    "description": "Get your clothes professionally ironed and pressed to perfection.",
                    "instructions": "Please specify any special folding or hanging preferences.",
                    "base_price": "20.00",
                    "is_taxable": True,
                    "min_processing_duration": 24,
                    "max_processing_duration": 48,
                    "duration_unit": "hours",
                    "is_active": True,
                    "is_featured": True,
                    "display_order": 3
                }
            }
        ]

        # Create service variants
        variants = [
            # Wash & Fold variants
            {
                "model": "services.servicevariant",
                "pk": 1,
                "fields": {
                    "service": 1,
                    "name": "Regular (24h)",
                    "description": "Standard processing time",
                    "price_adjustment": "0.00",
                    "is_default": True,
                    "is_active": True
                }
            },
            {
                "model": "services.servicevariant",
                "pk": 2,
                "fields": {
                    "service": 1,
                    "name": "Express (12h)",
                    "description": "Faster processing time",
                    "price_adjustment": "5.00",
                    "is_default": False,
                    "is_active": True
                }
            },
            # Dry Cleaning variants
            {
                "model": "services.servicevariant",
                "pk": 3,
                "fields": {
                    "service": 2,
                    "name": "Standard (48h)",
                    "description": "Standard dry cleaning service",
                    "price_adjustment": "0.00",
                    "is_default": True,
                    "is_active": True
                }
            },
            # Ironing variants
            {
                "model": "services.servicevariant",
                "pk": 4,
                "fields": {
                    "service": 3,
                    "name": "Standard (24h)",
                    "description": "Standard ironing service",
                    "price_adjustment": "0.00",
                    "is_default": True,
                    "is_active": True
                }
            },
            {
                "model": "services.servicevariant",
                "pk": 5,
                "fields": {
                    "service": 3,
                    "name": "Express (Same Day)",
                    "description": "Same day ironing service",
                    "price_adjustment": "10.00",
                    "is_default": False,
                    "is_active": True
                }
            }
        ]

        # Create service options
        options = [
            {
                "model": "services.serviceoption",
                "pk": 1,
                "fields": {
                    "service": 1,
                    "name": "Fabric Softener",
                    "description": "Add fabric softener to your laundry",
                    "option_type": "checkbox",
                    "price_adjustment": "2.00",
                    "is_required": False,
                    "is_active": True,
                    "display_order": 1
                }
            },
            {
                "model": "services.serviceoption",
                "pk": 2,
                "fields": {
                    "service": 1,
                    "name": "Scent Boost",
                    "description": "Add extra fragrance to your laundry",
                    "option_type": "checkbox",
                    "price_adjustment": "1.50",
                    "is_required": False,
                    "is_active": True,
                    "display_order": 2
                }
            }
        ]

        # Combine all data
        data = categories + services + variants + options

        # Write to file
        with open('initial_data.json', 'w') as f:
            json.dump(data, f, indent=2)

        self.stdout.write(self.style.SUCCESS('Successfully created initial data in initial_data.json'))
