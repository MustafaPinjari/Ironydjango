from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.urls import reverse
from decimal import Decimal
import uuid


class ServiceCategory(models.Model):
    """Category for grouping services (e.g., Laundry, Dry Cleaning, Ironing)."""
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    icon = models.CharField(_('icon class'), max_length=50, blank=True, 
                          help_text=_('Icon class from your icon font (e.g., fas fa-tshirt)'))
    is_active = models.BooleanField(_('is active'), default=True)
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    
    class Meta:
        verbose_name = _('service category')
        verbose_name_plural = _('service categories')
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('services:category_detail', kwargs={'slug': self.slug})


class Service(models.Model):
    """Main service model representing different types of laundry services."""
    class ServiceType(models.TextChoices):
        WASH_FOLD = 'wash_fold', _('Wash & Fold')
        DRY_CLEAN = 'dry_clean', _('Dry Cleaning')
        IRONING = 'ironing', _('Ironing')
        SPECIAL = 'special', _('Special Treatment')
        ALTERATION = 'alteration', _('Alteration')
    
    class DurationUnit(models.TextChoices):
        HOURS = 'hours', _('Hours')
        DAYS = 'days', _('Days')
        WEEKS = 'weeks', _('Weeks')
    
    # Basic information
    name = models.CharField(_('service name'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, unique=True)
    service_type = models.CharField(
        _('service type'),
        max_length=20,
        choices=ServiceType.choices,
        default=ServiceType.WASH_FOLD
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services',
        verbose_name=_('category')
    )
    
    # Description and details
    short_description = models.TextField(_('short description'), max_length=255, blank=True)
    description = models.TextField(_('detailed description'), blank=True)
    instructions = models.TextField(_('care instructions'), blank=True)
    
    # Pricing and timing
    base_price = models.DecimalField(
        _('base price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_taxable = models.BooleanField(_('is taxable'), default=True)
    min_processing_duration = models.PositiveIntegerField(_('minimum processing duration'), default=1)
    max_processing_duration = models.PositiveIntegerField(_('maximum processing duration'), default=3)
    duration_unit = models.CharField(
        _('duration unit'),
        max_length=10,
        choices=DurationUnit.choices,
        default=DurationUnit.DAYS
    )
    
    # Display and availability
    is_active = models.BooleanField(_('is active'), default=True)
    is_featured = models.BooleanField(_('featured service'), default=False)
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    
    # Images
    image = models.ImageField(
        _('service image'),
        upload_to='services/',
        null=True,
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('service')
        verbose_name_plural = _('services')
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['service_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.name)}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('services:service_detail', kwargs={'slug': self.slug})
    
    def get_processing_time_display(self):
        if self.min_processing_duration == self.max_processing_duration:
            return f"{self.min_processing_duration} {self.get_duration_unit_display().lower()}"
        return (
            f"{self.min_processing_duration}-{self.max_processing_duration} "
            f"{self.get_duration_unit_display().lower()}"
        )


class ServiceVariant(models.Model):
    """Variants for services (e.g., different materials, weights, or treatments)."""
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_('service')
    )
    name = models.CharField(_('variant name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    price_adjustment = models.DecimalField(
        _('price adjustment'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_('Additional cost (or discount if negative) for this variant')
    )
    sku = models.CharField(_('SKU'), max_length=50, blank=True, unique=True)
    is_default = models.BooleanField(_('is default'), default=False)
    is_active = models.BooleanField(_('is active'), default=True)
    
    class Meta:
        verbose_name = _('service variant')
        verbose_name_plural = _('service variants')
        ordering = ['service', 'name']
        unique_together = [['service', 'name']]
    
    def __str__(self):
        return f"{self.service.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.sku:
            base_sku = f"{self.service_id}-{slugify(self.name).replace('-', '')}"
            self.sku = base_sku.upper()
        
        # Ensure only one default variant per service
        if self.is_default:
            ServiceVariant.objects.filter(
                service=self.service, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)


class ServiceOption(models.Model):
    """Additional options that can be added to a service (e.g., fragrance, starch level)."""
    class OptionType(models.TextChoices):
        CHECKBOX = 'checkbox', _('Checkbox (Yes/No)')
        SELECT = 'select', _('Select from list')
        MULTISELECT = 'multiselect', _('Select multiple')
        NUMBER = 'number', _('Numeric value')
        TEXT = 'text', _('Text input')
    
    name = models.CharField(_('option name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    option_type = models.CharField(
        _('option type'),
        max_length=20,
        choices=OptionType.choices,
        default=OptionType.CHECKBOX
    )
    price_adjustment = models.DecimalField(
        _('price adjustment'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_('Additional cost (or discount if negative) for this option')
    )
    is_required = models.BooleanField(_('is required'), default=False)
    is_active = models.BooleanField(_('is active'), default=True)
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    
    # Relationships
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name=_('service')
    )
    
    class Meta:
        verbose_name = _('service option')
        verbose_name_plural = _('service options')
        ordering = ['service', 'display_order', 'name']
    
    def __str__(self):
        return f"{self.service.name} - {self.name}"


class ServiceOptionChoice(models.Model):
    """Available choices for SELECT or MULTISELECT option types."""
    option = models.ForeignKey(
        ServiceOption,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name=_('option')
    )
    name = models.CharField(_('choice name'), max_length=100)
    value = models.CharField(_('value'), max_length=100)
    price_adjustment = models.DecimalField(
        _('price adjustment'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_('Additional cost (or discount if negative) for this choice')
    )
    is_default = models.BooleanField(_('is default'), default=False)
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    
    class Meta:
        verbose_name = _('option choice')
        verbose_name_plural = _('option choices')
        ordering = ['option', 'display_order', 'name']
        unique_together = [['option', 'value']]
    
    def __str__(self):
        return f"{self.option.name}: {self.name}"


class ServiceImage(models.Model):
    """Additional images for a service."""
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('service')
    )
    image = models.ImageField(
        _('image'),
        upload_to='service_images/'
    )
    alt_text = models.CharField(
        _('alternative text'),
        max_length=255,
        blank=True,
        help_text=_('Alternative text for accessibility (required for WCAG)')
    )
    caption = models.CharField(_('caption'), max_length=200, blank=True)
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    is_featured = models.BooleanField(_('featured image'), default=False)
    
    class Meta:
        verbose_name = _('service image')
        verbose_name_plural = _('service images')
        ordering = ['service', 'display_order']
    
    def __str__(self):
        return f"{self.service.name} - {self.alt_text or 'Image'}"
    
    def save(self, *args, **kwargs):
        if not self.alt_text and self.caption:
            self.alt_text = self.caption
        super().save(*args, **kwargs)


class ServiceFAQ(models.Model):
    """Frequently asked questions for services."""
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='faqs',
        verbose_name=_('service')
    )
    question = models.CharField(_('question'), max_length=255)
    answer = models.TextField(_('answer'))
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    is_active = models.BooleanField(_('is active'), default=True)
    
    class Meta:
        verbose_name = _('service FAQ')
        verbose_name_plural = _('service FAQs')
        ordering = ['service', 'display_order', 'question']
    
    def __str__(self):
        return f"{self.service.name}: {self.question[:50]}"
