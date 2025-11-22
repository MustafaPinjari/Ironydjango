from django.core.management.base import BaseCommand
from services.models import Service, ServiceVariant, ServiceOption

class Command(BaseCommand):
    help = 'Creates sample data for services, variants and options'

    def handle(self, *args, **options):
        # Create Laundry Service
        laundry = Service.objects.create(
            name='Laundry',
            description='Professional laundry service',
            base_price=10.00,
            is_active=True
        )

        # Create Dry Cleaning Service
        dry_cleaning = Service.objects.create(
            name='Dry Cleaning',
            description='Professional dry cleaning service',
            base_price=15.00,
            is_active=True
        )

        # Create Ironing Service
        ironing = Service.objects.create(
            name='Ironing',
            description='Professional ironing service',
            base_price=8.00,
            is_active=True
        )

        # Create Laundry Variants
        ServiceVariant.objects.create(
            service=laundry,
            name='Regular',
            description='Standard laundry service (2-3 days)',
            price_adjustment=0.00,
            is_active=True,
            is_default=True
        )
        
        express_laundry = ServiceVariant.objects.create(
            service=laundry,
            name='Express',
            description='Same day laundry service',
            price_adjustment=5.00,
            is_active=True
        )

        # Create Dry Cleaning Variants
        ServiceVariant.objects.create(
            service=dry_cleaning,
            name='Standard',
            description='Standard dry cleaning (3-4 days)',
            price_adjustment=0.00,
            is_active=True,
            is_default=True
        )
        
        express_dry_clean = ServiceVariant.objects.create(
            service=dry_cleaning,
            name='Express',
            description='Next day dry cleaning',
            price_adjustment=7.00,
            is_active=True
        )

        # Create Ironing Variants
        ServiceVariant.objects.create(
            service=ironing,
            name='Standard',
            description='Standard ironing (2-3 days)',
            price_adjustment=0.00,
            is_active=True,
            is_default=True
        )
        
        express_ironing = ServiceVariant.objects.create(
            service=ironing,
            name='Express',
            description='Same day ironing',
            price_adjustment=4.00,
            is_active=True
        )

        # Create Service Options
        stain_removal = ServiceOption.objects.create(
            service=laundry,  # This option is available for laundry service
            name='Stain Removal',
            description='Special stain treatment',
            price_adjustment=3.00,
            option_type='checkbox',
            is_active=True
        )
        
        fabric_softener = ServiceOption.objects.create(
            service=laundry,  # This option is available for laundry service
            name='Fabric Softener',
            description='Add fabric softener',
            price_adjustment=1.50,
            option_type='checkbox',
            is_active=True
        )
        
        hanger_delivery = ServiceOption.objects.create(
            service=laundry,  # This option is available for laundry service
            name='Hanger Delivery',
            description='Clothes delivered on hangers',
            price_adjustment=2.00,
            option_type='checkbox',
            is_active=True
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))
