from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
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
    notes = models.TextField(_('special instructions'), blank=True, null=True)
    total_amount = models.DecimalField(
        _('total amount'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_orders',
        verbose_name=_('customer')
    )
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
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    pickup_address = models.TextField(_('pickup address'))
    delivery_address = models.TextField(_('delivery address'))
    special_instructions = models.TextField(_('special instructions'), blank=True, null=True)
    total_amount = models.DecimalField(
        _('total amount'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    payment_status = models.BooleanField(_('payment status'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    scheduled_pickup = models.DateTimeField(_('scheduled pickup'), null=True, blank=True)
    scheduled_delivery = models.DateTimeField(_('scheduled delivery'), null=True, blank=True)

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
        """Override save to calculate total amount before saving."""
        if not self.pk:  # New order
            self.total_amount = 0
        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        """Calculate total price before saving."""
        if not self.pk or 'unit_price' in kwargs.get('update_fields', []) or 'quantity' in kwargs.get('update_fields', []):
            self.unit_price = self.cloth_type.price_per_unit
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        # Update the order total when an item is saved
        self.order.total_amount = self.order.calculate_total()
        self.order.save(update_fields=['total_amount', 'updated_at'])
