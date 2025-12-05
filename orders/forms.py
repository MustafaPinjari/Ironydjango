from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.utils import timezone
from .models import Order, OrderItem, OrderStatusUpdate
from services.models import Service, ServiceVariant, ServiceOption
from django.utils.translation import gettext_lazy as _ 

# Import DeliveryType from the Order model
from .models import Order
DeliveryType = Order.DeliveryType

class OrderItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Remove user from kwargs to prevent passing it to parent's __init__
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set up the service choices - only active services
        self.fields['service'].queryset = Service.objects.filter(is_active=True).distinct()
        self.fields['service'].empty_label = "Select a service"
        self.fields['service'].widget.attrs.update({
            'class': 'form-select service-select',
            'data-url': '/api/services/variants/',
            'required': 'required'
        })
        
        # Set up variant field - will be populated via AJAX
        self.fields['variant'].queryset = ServiceVariant.objects.none()
        self.fields['variant'].empty_label = "Select a variant"
        self.fields['variant'].widget.attrs.update({
            'class': 'form-select variant-select',
            'required': 'required'
        })
        
        # Set up quantity field with default value
        if not self.initial.get('quantity'):
            self.fields['quantity'].initial = 1
        self.fields['quantity'].widget.attrs.update({
            'class': 'form-control quantity',
            'min': 1,
            'required': 'required'
        })
        
        # Set up options field - only active options
        self.fields['options'].queryset = ServiceOption.objects.filter(is_active=True).distinct()
        self.fields['options'].required = False
        self.fields['options'].widget = forms.CheckboxSelectMultiple()
        self.fields['options'].widget.attrs.update({
            'class': 'form-check-input',
            'data-url': '/api/options/'
        })
        
        # Set up description field
        self.fields['description'].required = False
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Any special instructions for this item (e.g., stain removal, special handling)...'
        })
        
        # If editing an existing item
        if self.instance and self.instance.pk and self.instance.service:
            self.fields['variant'].queryset = self.instance.service.variants.filter(is_active=True)
            
            # Set initial value for service to trigger variant loading
            self.fields['service'].initial = self.instance.service
            
            # Set initial values for options
            if hasattr(self.instance, 'options'):
                self.fields['options'].initial = self.instance.options.all()
        
        # Handle GET request with service_id
        if 'service' in self.data:
            try:
                service_id = int(self.data.get('service'))
                self.fields['variant'].queryset = ServiceVariant.objects.filter(service_id=service_id, is_active=True)
            except (ValueError, TypeError):
                pass
                
        # Handle POST request with service_id
        if self.data:
            service_id_key = f"{self.prefix}-service" if self.prefix else "service"
            variant_id_key = f"{self.prefix}-variant" if self.prefix else "variant"
            
            if service_id_key in self.data:
                try:
                    service_id = int(self.data.get(service_id_key))
                    self.fields['variant'].queryset = ServiceVariant.objects.filter(service_id=service_id, is_active=True)
                    
                    # If variant is already selected, validate it
                    if variant_id_key in self.data and self.data.get(variant_id_key):
                        variant_id = int(self.data.get(variant_id_key))
                        # Validate that the variant belongs to the selected service
                        if not ServiceVariant.objects.filter(id=variant_id, service_id=service_id, is_active=True).exists():
                            self.add_error('variant', 'Select a valid choice. That choice is not one of the available choices.')
                except (ValueError, TypeError):
                    pass
    
    class Meta:
        model = OrderItem
        fields = ['service', 'variant', 'quantity', 'options', 'description']
        help_texts = {
            'service': 'Select the type of service you need',
            'variant': 'Choose the specific variant of the service',
            'quantity': 'Number of items',
            'options': 'Select any additional options',
            'description': 'Add any special instructions for this item'
        }
    
    def clean_variant(self):
        """Ensure the selected variant is valid for the selected service."""
        service = self.cleaned_data.get('service')
        variant = self.cleaned_data.get('variant')
        
        if service and variant:
            # Check that the variant belongs to the selected service
            if variant.service != service:
                raise forms.ValidationError("The selected variant is not valid for the chosen service.")
        
        return variant
    
    def clean_quantity(self):
        """Ensure quantity is a positive integer."""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("Quantity must be a positive number.")
        return quantity


class BaseOrderItemFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def _construct_form(self, i, **kwargs):
        if self.user:
            kwargs['user'] = self.user
        return super()._construct_form(i, **kwargs)
    
    def clean(self):
        super().clean()
        # Ensure at least one item is provided
        if any(self.errors):
            return
        if not any(cleaned_data and not cleaned_data.get('DELETE', False) 
                  for cleaned_data in self.cleaned_data):
            raise forms.ValidationError('You must add at least one item to the order.')


# Create the formset factory
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    formset=BaseOrderItemFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)


class OrderForm(forms.ModelForm):
    # Explicitly define all form fields as class-level fields
    delivery_type = forms.ChoiceField(
        choices=Order.DeliveryType.choices,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
            'data-toggle': 'collapse',
            'data-target': '.delivery-fields',
            'hx-get': '/orders/update-form-fields/',
            'hx-trigger': 'change',
            'hx-target': '#order-fields',
            'hx-swap': 'innerHTML'
        }),
        initial=Order.DeliveryType.PICKUP,
        required=True,
        label=_('Delivery Type'),
        help_text=_('Choose whether you want to pick up the order or have it delivered')
    )
    
    pickup_address = forms.CharField(
        label=_('Pickup Address'),
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter pickup address',
            'rows': 2
        })
    )
    
    delivery_address = forms.CharField(
        label=_('Delivery Address'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter delivery address',
            'rows': 2
        })
    )
    
    preferred_pickup_date = forms.DateField(
        label=_('Preferred Pickup Date'),
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text=_('When would you like to pick up your order?')
    )
    
    preferred_delivery_date = forms.DateField(
        label=_('Preferred Delivery Date'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text=_('When would you like your order to be delivered?')
    )
    
    special_instructions = forms.CharField(
        label=_('Special Instructions'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special instructions for your order...'
        })
    )
    
    class Meta:
        model = Order
        fields = [
            'delivery_type', 
            'pickup_address', 
            'delivery_address', 
            'preferred_pickup_date',
            'preferred_delivery_date',
            'special_instructions'
        ]
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set minimum date to today
        today = timezone.now().date()
        
        # Set min date for date fields
        self.fields['preferred_pickup_date'].widget.attrs['min'] = today.strftime('%Y-%m-%d')
        self.fields['preferred_delivery_date'].widget.attrs['min'] = today.strftime('%Y-%m-%d')
        
        # Set user-specific defaults if needed
        if self.user and self.user.is_authenticated and not self.instance.pk:
            if hasattr(self.user, 'profile') and hasattr(self.user.profile, 'address'):
                self.fields['pickup_address'].initial = self.user.profile.address
            elif hasattr(self.user, 'address'):
                self.fields['pickup_address'].initial = self.user.address
        
        # Set initial field requirements based on delivery type
        self.update_field_requirements()
    
    def update_field_requirements(self):
        """Update field requirements based on delivery type"""
        # Get delivery type from form data or initial data, default to PICKUP
        delivery_type = self.data.get('delivery_type', 
                                   self.initial.get('delivery_type', 
                                                  Order.DeliveryType.PICKUP))
        
        if delivery_type == Order.DeliveryType.DELIVERY:
            self.fields['delivery_address'].required = True
            self.fields['preferred_delivery_date'].required = True
            self.fields['pickup_address'].required = False
            self.fields['preferred_pickup_date'].required = False
        else:  # PICKUP
            self.fields['pickup_address'].required = True
            self.fields['preferred_pickup_date'].required = True
            self.fields['delivery_address'].required = False
            self.fields['preferred_delivery_date'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        delivery_type = cleaned_data.get('delivery_type')
        
        if delivery_type == Order.DeliveryType.DELIVERY:
            if not cleaned_data.get('delivery_address'):
                self.add_error('delivery_address', 'This field is required for delivery orders.')
            if not cleaned_data.get('preferred_delivery_date'):
                self.add_error('preferred_delivery_date', 'This field is required for delivery orders.')
        else:  # PICKUP
            if not cleaned_data.get('pickup_address'):
                self.add_error('pickup_address', 'This field is required for pickup orders.')
            if not cleaned_data.get('preferred_pickup_date'):
                self.add_error('preferred_pickup_date', 'This field is required for pickup orders.')
        
        return cleaned_data
    
    class Meta:
        model = Order
        fields = [
            'delivery_type', 
            'pickup_address', 
            'delivery_address', 
            'preferred_pickup_date',
            'preferred_delivery_date',
            'special_instructions'
        ]
        widgets = {
            'pickup_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter pickup address',
                'required': 'required'
            }),
            'delivery_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter delivery address',
                'required': False
            }),
            'preferred_pickup_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'type': 'date',
                'required': 'required'
            }),
            'preferred_delivery_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'type': 'date',
                'required': False
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special instructions for your order...',
                'required': False
            }),
        }
