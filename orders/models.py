from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings

class ClothType(models.Model):
    """Model to store different types of clothes and their pricing."""
    name = models.CharField(_('cloth type'), max_length=100)
    description = models.TextField(_('description'), blank=True, null=True)
    price_per_unit = models.DecimalField(
        _('price per unit'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('cloth type')
        verbose_name_plural = _('cloth types')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - ${self.price_per_unit}"

class Order(models.Model):
    """Model to store laundry service orders."""
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        READY_FOR_PICKUP = 'READY_FOR_PICKUP', _('Ready for Pickup')
        PICKED_UP = 'PICKED_UP', _('Picked Up')
        DELIVERED = 'DELIVERED', _('Delivered')
        CANCELLED = 'CANCELLED', _('Cancelled')
        REJECTED = 'REJECTED', _('Rejected')
    
    class ServiceType(models.TextChoices):
        WASH_AND_FOLD = 'WASH_AND_FOLD', _('Wash & Fold')
        WASH_AND_IRON = 'WASH_AND_IRON', _('Wash & Iron')
        DRY_CLEANING = 'DRY_CLEANING', _('Dry Cleaning')
        IRONING = 'IRONING', _('Ironing Only')

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_orders',
        verbose_name=_('customer')
    )
    service_type = models.CharField(
        _('service type'),
        max_length=20,
        choices=ServiceType.choices,
        default=ServiceType.WASH_AND_FOLD
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    pickup_address = models.TextField(_('pickup address'))
    delivery_address = models.TextField(_('delivery address'))
    pickup_date = models.DateTimeField(_('pickup date'))
    delivery_date = models.DateTimeField(_('delivery date'))
    special_instructions = models.TextField(_('special instructions'), blank=True, null=True)
    total_amount = models.DecimalField(
        _('total amount'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    payment_status = models.BooleanField(_('payment status'), default=False)
    press_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_orders',
        null=True,
        blank=True,
        verbose_name=_('press person')
    )
    delivery_partner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='delivery_orders',
        null=True,
        blank=True,
        verbose_name=_('delivery partner')
    )
    scheduled_pickup = models.DateTimeField(_('scheduled pickup'), null=True, blank=True)
    scheduled_delivery = models.DateTimeField(_('scheduled delivery'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.get_status_display()}"
        
    def update_total(self):
        """Update the total amount of the order based on its items."""
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount', 'updated_at'])
        return total
        
    def get_absolute_url(self):
        return reverse('orders:detail', kwargs={'pk': self.pk})

    def calculate_total(self):
        """Calculate the total amount based on order items."""
        return sum(item.total_price for item in self.items.all())

    def save(self, *args, **kwargs):
        """Override save to handle order saving logic."""
        is_new = not self.pk
        
        # For new orders, set initial status and timestamps
        if is_new:
            self.status = self.Status.PENDING
            
        # Calculate total from items if this is an update
        if not is_new and not kwargs.get('skip_update_total', False):
            self.total_amount = self.calculate_total()
            
        super().save(*args, **kwargs)
        
        # Update related items if needed
        if not is_new and hasattr(self, '_order_items_to_update'):
            for item in self._order_items_to_update:
                item.order = self
                item.save()
            delattr(self, '_order_items_to_update')

class OrderItem(models.Model):
    """Model to store individual items within an order."""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('order')
    )
    cloth_type = models.ForeignKey(
        ClothType,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_('cloth type')
    )
    quantity = models.PositiveIntegerField(_('quantity'), default=1)
    unit_price = models.DecimalField(
        _('unit price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    total_price = models.DecimalField(
        _('total price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    special_instructions = models.TextField(_('special instructions'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quantity}x {self.cloth_type.name} - ${self.total_price}"

    def clean(self):
        """Validate the order item before saving."""
        # First check if we have a cloth_type_id to avoid RelatedObjectDoesNotExist
        if not hasattr(self, 'cloth_type') or not self.cloth_type_id:
            raise ValidationError({
                'cloth_type': 'Please select a cloth type.'
            })
            
        # Now we can safely access self.cloth_type since we know it exists
        try:
            # Validate cloth_type is active for new items
            if not self.pk and not self.cloth_type.is_active:
                raise ValidationError({
                    'cloth_type': 'This cloth type is not available.'
                })
        except ClothType.DoesNotExist:
            raise ValidationError({
                'cloth_type': 'Selected cloth type does not exist.'
            })
            
        # Validate quantity is at least 1
        if not hasattr(self, 'quantity') or self.quantity < 1:
            raise ValidationError({
                'quantity': 'Quantity must be at least 1.'
            })
            
        # Ensure unit price is set from cloth type if not provided
        if not self.unit_price and self.cloth_type:
            self.unit_price = self.cloth_type.price_per_unit
            
        # Calculate total price
        if self.unit_price is not None and self.quantity is not None:
            self.total_price = self.unit_price * self.quantity
    
    def save(self, *args, **kwargs):
        """Save the order item with proper validation and update order total."""
        self.full_clean()
        
        # If this is a new item, save it first to get an ID
        is_new = not self.pk
        if is_new and self.order_id:
            super().save(*args, **kwargs)
            
        # Update the order's total amount
        if self.order_id:
            # Use a more efficient way to update the order total
            self.order.update_total()
            
        # If this is an existing item, save it after updating the order
        if not is_new or not self.order_id:
            super().save(*args, **kwargs)
