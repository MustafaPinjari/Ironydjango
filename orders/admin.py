from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('total_price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at', 'payment_status')
    search_fields = ('order_number', 'customer__email', 'customer__first_name', 'customer__last_name')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'unit_price', 'total_price', 'order')
    list_filter = ('created_at', 'status')
    search_fields = ('name', 'description', 'order__order_number')
    list_select_related = ('order', 'service')
    readonly_fields = ('created_at', 'updated_at', 'total_price')
