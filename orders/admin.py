from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem, ClothType

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_total_price',)
    fields = ('cloth_type', 'quantity', 'unit_price', 'get_total_price', 'special_instructions')
    
    def get_total_price(self, obj):
        return f"${obj.total_price}"
    get_total_price.short_description = _('Total Price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_link', 'status', 'total_amount_display', 'created_at', 'updated_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('id', 'customer__email', 'customer__first_name', 'customer__last_name')
    readonly_fields = ('created_at', 'updated_at', 'total_amount_display')
    inlines = [OrderItemInline]
    fieldsets = (
        (_('Order Information'), {
            'fields': ('customer', 'status', 'total_amount_display', 'payment_status')
        }),
        (_('Staff Assignment'), {
            'fields': ('press_person', 'delivery_partner')
        }),
        (_('Address Information'), {
            'fields': ('pickup_address', 'delivery_address', 'special_instructions')
        }),
        (_('Scheduling'), {
            'fields': ('scheduled_pickup', 'scheduled_delivery')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def customer_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.customer.id])
        return mark_safe(f'<a href="{url}">{obj.customer.get_full_name() or obj.customer.email}</a>')
    customer_link.short_description = _('Customer')
    customer_link.admin_order_field = 'customer__email'
    
    def total_amount_display(self, obj):
        return f"${obj.total_amount}"
    total_amount_display.short_description = _('Total Amount')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'customer', 'press_person', 'delivery_partner'
        )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_link', 'cloth_type', 'quantity', 'unit_price_display', 'total_price_display')
    list_filter = ('cloth_type',)
    search_fields = ('order__id', 'cloth_type__name')
    
    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return mark_safe(f'<a href="{url}">Order #{obj.order.id}</a>')
    order_link.short_description = _('Order')
    order_link.admin_order_field = 'order__id'
    
    def unit_price_display(self, obj):
        return f"${obj.unit_price}"
    unit_price_display.short_description = _('Unit Price')
    
    def total_price_display(self, obj):
        return f"${obj.total_price}"
    total_price_display.short_description = _('Total Price')

@admin.register(ClothType)
class ClothTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_unit_display', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    
    def price_per_unit_display(self, obj):
        return f"${obj.price_per_unit}"
    price_per_unit_display.short_description = _('Price per Unit')
    
    def save_model(self, request, obj, form, change):
        # If price changes, update all related order items
        if change and 'price_per_unit' in form.changed_data:
            from django.db.models import F
            OrderItem.objects.filter(
                cloth_type=obj,
                order__status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS']
            ).update(
                unit_price=obj.price_per_unit,
                total_price=F('quantity') * obj.price_per_unit
            )
        super().save_model(request, obj, form, change)
