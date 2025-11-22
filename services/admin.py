from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import (
    ServiceCategory, Service, ServiceVariant, ServiceOption, 
    ServiceOptionChoice, ServiceImage, ServiceFAQ
)


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1
    fields = ('image', 'image_preview', 'alt_text', 'caption', 'display_order', 'is_featured')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />', 
                obj.image.url
            )
        return "No image"
    image_preview.short_description = _('Preview')


class ServiceVariantInline(admin.TabularInline):
    model = ServiceVariant
    extra = 1
    fields = ('name', 'price_adjustment', 'is_default', 'is_active')


class ServiceOptionInline(admin.TabularInline):
    model = ServiceOption
    extra = 1
    fields = ('name', 'option_type', 'price_adjustment', 'is_required', 'is_active')
    show_change_link = True


class ServiceOptionChoiceInline(admin.TabularInline):
    model = ServiceOptionChoice
    extra = 1
    fields = ('name', 'value', 'price_adjustment', 'is_default', 'display_order')


class ServiceFAQInline(admin.TabularInline):
    model = ServiceFAQ
    extra = 1
    fields = ('question', 'answer', 'is_active', 'display_order')


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order', 'service_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'display_order')
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _service_count=models.Count('services')
        )
    
    def service_count(self, obj):
        return obj._service_count
    service_count.short_description = _('Services')
    service_count.admin_order_field = '_service_count'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'service_type', 'base_price', 
        'processing_time', 'is_active', 'is_featured'
    )
    list_filter = ('is_active', 'is_featured', 'service_type', 'category')
    search_fields = ('name', 'description', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'is_featured', 'base_price')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ()
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'service_type', 'category', 'is_active', 'is_featured')
        }),
        (_('Descriptions'), {
            'fields': ('short_description', 'description', 'instructions')
        }),
        (_('Pricing & Timing'), {
            'fields': (
                'base_price', 'is_taxable',
                ('min_processing_duration', 'max_processing_duration', 'duration_unit')
            )
        }),
        (_('Images'), {
            'fields': ('image',)
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [
        ServiceImageInline,
        ServiceVariantInline,
        ServiceOptionInline,
        ServiceFAQInline,
    ]
    
    def processing_time(self, obj):
        return obj.get_processing_time_display()
    processing_time.short_description = _('Processing Time')


@admin.register(ServiceVariant)
class ServiceVariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'price_adjustment', 'is_default', 'is_active')
    list_filter = ('is_active', 'is_default', 'service__category')
    search_fields = ('name', 'service__name', 'description')
    list_editable = ('price_adjustment', 'is_default', 'is_active')
    list_select_related = ('service', 'service__category')
    
    fieldsets = (
        (None, {
            'fields': ('service', 'name', 'description', 'is_active')
        }),
        (_('Pricing'), {
            'fields': ('price_adjustment', 'is_default')
        }),
        (_('Inventory'), {
            'fields': ('sku',)
        }),
    )


@admin.register(ServiceOption)
class ServiceOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'option_type', 'price_adjustment', 'is_required', 'is_active')
    list_filter = ('option_type', 'is_required', 'is_active', 'service__category')
    search_fields = ('name', 'service__name', 'description')
    list_editable = ('is_required', 'is_active', 'price_adjustment')
    list_select_related = ('service', 'service__category')
    inlines = [ServiceOptionChoiceInline]
    
    fieldsets = (
        (None, {
            'fields': ('service', 'name', 'description')
        }),
        (_('Configuration'), {
            'fields': ('option_type', 'is_required', 'is_active', 'display_order')
        }),
        (_('Pricing'), {
            'fields': ('price_adjustment',)
        }),
    )


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ('service', 'image_preview', 'is_featured', 'display_order')
    list_filter = ('is_featured', 'service__category')
    list_editable = ('is_featured', 'display_order')
    search_fields = ('service__name', 'alt_text', 'caption')
    list_select_related = ('service', 'service__category')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />', 
                obj.image.url
            )
        return "No image"
    image_preview.short_description = _('Preview')


@admin.register(ServiceFAQ)
class ServiceFAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'service', 'is_active', 'display_order')
    list_filter = ('is_active', 'service__category')
    search_fields = ('question', 'answer', 'service__name')
    list_editable = ('is_active', 'display_order')
    list_select_related = ('service', 'service__category')
    
    fieldsets = (
        (None, {
            'fields': ('service', 'question', 'answer')
        }),
        (_('Display'), {
            'fields': ('is_active', 'display_order')
        }),
    )
