from rest_framework import serializers
from .models import Service, ServiceVariant, ServiceOption

class ServiceVariantSerializer(serializers.ModelSerializer):
    """Serializer for ServiceVariant model."""
    final_price = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceVariant
        fields = ['id', 'name', 'description', 'price_adjustment', 'is_active', 'final_price']
        read_only_fields = ['final_price']
    
    def get_final_price(self, obj):
        # Calculate final price by adding base price and adjustment
        return float(obj.service.base_price + obj.price_adjustment)

class ServiceOptionSerializer(serializers.ModelSerializer):
    """Serializer for ServiceOption model."""
    class Meta:
        model = ServiceOption
        fields = ['id', 'name', 'description', 'price_adjustment', 'is_active']

class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model with nested variants and options."""
    variants = ServiceVariantSerializer(many=True, read_only=True)
    options = ServiceOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'base_price', 'is_active', 'variants', 'options']
