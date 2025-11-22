from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.utils import timezone
from .models import Order, OrderItem
from services.models import Service, ServiceVariant, ServiceOption

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
            'data-url': '/api/services/',
            'required': 'required'
        })
        
        # Set up variant field - will be populated via AJAX
        self.fields['variant'].queryset = ServiceVariant.objects.none()
        self.fields['variant'].empty_label = "Select a variant"
        self.fields['variant'].widget.attrs.update({
            'class': 'form-select variant-select',
            'data-url': '/api/variants/'
        })
        
        # Set up quantity field
        self.fields['quantity'].initial = 1
        self.fields['quantity'].widget.attrs.update({
            'class': 'form-control quantity',
            'min': 1,
            'required': 'required'
        })
        
        # Set up options field - only active options
        self.fields['options'].queryset = ServiceOption.objects.filter(is_active=True).distinct()
        self.fields['options'].required = False
        self.fields['options'].widget.attrs.update({
            'class': 'form-check-input option-select',
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

    def __init__(self, *args, **kwargs):
        # Remove user from kwargs to prevent passing it to parent's __init__
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set up the querysets
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['variant'].queryset = ServiceVariant.objects.none()
        self.fields['options'].queryset = ServiceOption.objects.filter(is_active=True)
        
        # If we're editing an existing item
        if self.instance and self.instance.pk:
            if self.instance.service:
                self.fields['variant'].queryset = self.instance.service.variants.filter(is_active=True)
        
        # Add data attributes for dynamic loading
        if 'service' in self.data:
            try:
                service_id = int(self.data.get('service'))
                self.fields['variant'].queryset = ServiceVariant.objects.filter(service_id=service_id, is_active=True)
            except (ValueError, TypeError):
                pass


class BaseOrderItemFormSet(BaseInlineFormSet):
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
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set minimum date to today
        today = timezone.now().date()
        self.fields['preferred_pickup_date'].widget.attrs['min'] = today
        self.fields['preferred_delivery_date'].widget.attrs['min'] = today
        
        # Make delivery date not required initially
        self.fields['preferred_delivery_date'].required = False
        
        # Set user-specific defaults if needed
        if self.user and self.user.is_authenticated and not self.instance.pk:
            # Safely get the address if it exists
            if hasattr(self.user, 'profile') and hasattr(self.user.profile, 'address'):
                self.fields['pickup_address'].initial = self.user.profile.address
            elif hasattr(self.user, 'address'):
                # Fallback to user.address if it exists
                self.fields['pickup_address'].initial = self.user.address
    
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
            'delivery_type': forms.RadioSelect(attrs={
                'class': 'form-check-input delivery-type',
                'data-toggle': 'collapse',
                'data-target': '.delivery-fields'
            }),
            'pickup_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter pickup address'
            }),
            'delivery_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter delivery address'
            }),
            'preferred_pickup_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'type': 'date'
            }),
            'preferred_delivery_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'type': 'date'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special instructions for your order...'
            }),
        }
