from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from accounts.models import User
from services.models import Service, ServiceVariant, ServiceOption

class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PENDING = 'pending', _('Pending Payment')
        CONFIRMED = 'confirmed', _('Confirmed')
        PROCESSING = 'processing', _('In Progress')
        READY = 'ready', _('Ready for Pickup/Delivery')
        OUT_FOR_DELIVERY = 'out_for_delivery', _('Out for Delivery')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
        REFUNDED = 'refunded', _('Refunded')
        FAILED = 'failed', _('Failed')
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        AUTHORIZED = 'authorized', _('Authorized')
        PAID = 'paid', _('Paid')
        PARTIALLY_REFUNDED = 'partially_refunded', _('Partially Refunded')
        REFUNDED = 'refunded', _('Refunded')
        VOIDED = 'voided', _('Voided')
        FAILED = 'failed', _('Failed')
    
    class DeliveryType(models.TextChoices):
        PICKUP = 'pickup', _('Pickup')
        DELIVERY = 'delivery', _('Delivery')

    # Order information
    customer = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='orders',
        verbose_name=_('customer')
    )
    order_number = models.CharField(
        _('order number'),
        max_length=20,
        unique=True,
        db_index=True
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True
    )
    payment_status = models.CharField(
        _('payment status'),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True
    )
    
    # Delivery information
    delivery_type = models.CharField(
        _('delivery type'),
        max_length=10,
        choices=DeliveryType.choices,
        default=DeliveryType.PICKUP
    )
    pickup_address = models.TextField(_('pickup address'), blank=True)
    delivery_address = models.TextField(_('delivery address'), blank=True)
    preferred_pickup_date = models.DateField(_('preferred pickup date'), null=True, blank=True)
    preferred_delivery_date = models.DateField(_('preferred delivery date'), null=True, blank=True)
    
    # Financials
    subtotal = models.DecimalField(
        _('subtotal'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tax_amount = models.DecimalField(
        _('tax amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    shipping_cost = models.DecimalField(
        _('shipping cost'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_amount = models.DecimalField(
        _('discount amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_amount = models.DecimalField(
        _('total amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Staff assignments
    assigned_staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders',
        verbose_name=_('assigned staff')
    )
    delivery_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_orders',
        verbose_name=_('delivery person')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    confirmed_at = models.DateTimeField(_('confirmed at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    cancelled_at = models.DateTimeField(_('cancelled at'), null=True, blank=True)
    
    # Additional info
    special_instructions = models.TextField(_('special instructions'), blank=True)
    internal_notes = models.TextField(_('internal notes'), blank=True)
    cancellation_reason = models.TextField(_('cancellation reason'), blank=True)
    
    # Payment info
    payment_method = models.CharField(_('payment method'), max_length=50, blank=True)
    payment_reference = models.CharField(_('payment reference'), max_length=100, blank=True)
    payment_date = models.DateTimeField(_('payment date'), null=True, blank=True)

    def __str__(self):
        return f"Order {self.order_number} - {self.get_status_display()}"
        
    def save(self, *args, **kwargs):
        # First save to get a primary key
        if not self.pk:
            # Generate order number
            date_str = timezone.now().strftime('%y%m%d')
            last_order = Order.objects.filter(order_number__startswith=date_str).order_by('-id').first()
            if last_order:
                last_num = int(last_order.order_number.split('-')[-1])
                new_num = f"{date_str}-{str(last_num + 1).zfill(5)}"
            else:
                new_num = f"{date_str}-00001"
            self.order_number = new_num
            
            # Save the order first to get a primary key
            super().save(*args, **kwargs)
            
            # Now calculate totals and save again
            self.calculate_totals()
            super().save(update_fields=['subtotal', 'tax_amount', 'shipping_cost', 'total_amount'])
        else:
            # For existing orders, just update the totals and save
            self.calculate_totals()
            super().save(*args, **kwargs)
        
        # Update timestamps based on status changes
        if self.pk:
            try:
                old_status = Order.objects.get(pk=self.pk).status
                if self.status != old_status:
                    if self.status == self.Status.CONFIRMED and not self.confirmed_at:
                        self.confirmed_at = timezone.now()
                        self.save(update_fields=['confirmed_at'])
                    elif self.status == self.Status.COMPLETED and not self.completed_at:
                        self.completed_at = timezone.now()
                        self.save(update_fields=['completed_at'])
                    elif self.status == self.Status.CANCELLED and not self.cancelled_at:
                        self.cancelled_at = timezone.now()
                        self.save(update_fields=['cancelled_at'])
            except Order.DoesNotExist:
                pass
    
    def calculate_totals(self):
        """Calculate order totals based on items and other charges."""
        self.subtotal = sum(item.total_price for item in self.items.all())
        
        # Simple tax calculation (can be enhanced with tax rules)
        self.tax_amount = self.subtotal * Decimal('0.10')  # 10% tax
        
        # Shipping cost based on delivery type
        if self.delivery_type == self.DeliveryType.DELIVERY:
            self.shipping_cost = Decimal('5.00')  # Flat rate for now
        else:
            self.shipping_cost = Decimal('0.00')
            
        # Apply any discounts (simplified)
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
    
    def can_cancel(self):
        """Check if the order can be cancelled."""
        return self.status in [
            self.Status.PENDING,
            self.Status.CONFIRMED,
            self.Status.PROCESSING
        ]
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('orders:detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        related_name='items', 
        on_delete=models.CASCADE,
        verbose_name=_('order')
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_('service'),
        null=True,  # Make nullable for migration
        blank=True  # Make blank for forms
    )
    variant = models.ForeignKey(
        'services.ServiceVariant',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='order_items',
        verbose_name=_('variant')
    )
    options = models.ManyToManyField(
        'services.ServiceOption',
        related_name='order_items',
        blank=True,
        verbose_name=_('options')
    )
    
    # Item details
    name = models.CharField(
        _('item name'), 
        max_length=200,
        null=True,  # Make nullable for migration
        blank=True  # Make blank for forms
    )
    description = models.TextField(_('description'), blank=True)
    quantity = models.PositiveIntegerField(
        _('quantity'),
        default=1,
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        _('unit price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,  # Make nullable for migration
        blank=True  # Make blank for forms
    )
    
    # Additional charges/discounts
    discount_amount = models.DecimalField(
        _('discount amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Status tracking
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Order.Status.choices,
        default=Order.Status.PENDING
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)

    def __str__(self):
        return f"{self.quantity}x {self.name} (Order: {self.order.order_number})"
        
    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Set name and price from service if not set
        if not self.name and self.service:
            self.name = self.service.name
            if self.variant:
                self.name = f"{self.name} - {self.variant.name}"
        
        if not self.unit_price and self.service:
            self.unit_price = self.service.base_price
            if self.variant and self.variant.price_adjustment:
                self.unit_price += self.variant.price_adjustment
        
        # Update completion time if status changed to completed
        if self.pk:
            old_status = OrderItem.objects.get(pk=self.pk).status
            if self.status == Order.Status.COMPLETED and old_status != Order.Status.COMPLETED:
                self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def total_price(self):
        """Calculate the total price for this line item."""
        base_price = self.unit_price * self.quantity
        
        # Add any option prices
        option_prices = sum(option.price_adjustment for option in self.options.all())
        
        # Apply discount
        total = base_price + option_prices - self.discount_amount
        
        return max(total, Decimal('0.00'))  # Ensure we don't return negative amounts


class OrderStatusUpdate(models.Model):
    """
    Tracks changes to order status with timestamps and user who made the change.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_updates',
        verbose_name=_('order')
    )
    
    from_status = models.CharField(
        _('from status'),
        max_length=50,
        choices=Order.Status.choices,
        db_index=True
    )
    
    to_status = models.CharField(
        _('to status'),
        max_length=50,
        choices=Order.Status.choices,
        db_index=True
    )
    
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_status_changes',
        verbose_name=_('changed by')
    )
    
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True, db_index=True)
    
    notes = models.TextField(_('notes'), blank=True)
    
    # For tracking changes to other related models if needed
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('content type')
    )
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional metadata
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    
    class Meta:
        verbose_name = _('order status update')
        verbose_name_plural = _('order status updates')
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'
    
    def __str__(self):
        return f"{self.order.order_number}: {self.get_from_status_display()} → {self.get_to_status_display()}"
    
    def save(self, *args, **kwargs):
        # Auto-set the content_type if not set and we have a related object
        if not self.content_type_id and self.order_id:
            self.content_type = ContentType.objects.get_for_model(Order)
            self.object_id = self.order_id
        super().save(*args, **kwargs)
