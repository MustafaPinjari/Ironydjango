from django import forms
from django.forms import DateTimeInput, inlineformset_factory
from django.utils import timezone
from .models import Order, ClothType, OrderItem

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'service_type', 
            'pickup_address', 
            'delivery_address', 
            'pickup_date', 
            'delivery_date',
            'special_instructions'
        ]
        widgets = {
            'pickup_date': DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'delivery_date': DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'pickup_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'delivery_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'special_instructions': forms.Textarea({
                'rows': 3, 
                'class': 'form-control', 
                'placeholder': 'Any special instructions for your order...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set minimum date to current time + 1 hour
        min_date = (timezone.now() + timezone.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
        self.fields['pickup_date'].widget.attrs['min'] = min_date
        self.fields['delivery_date'].widget.attrs['min'] = min_date
        
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.widgets:
                field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        pickup_date = cleaned_data.get('pickup_date')
        delivery_date = cleaned_data.get('delivery_date')
        
        if pickup_date and delivery_date and delivery_date <= pickup_date:
            raise forms.ValidationError("Delivery date must be after pickup date.")
        
        return cleaned_data

class OrderItemForm(forms.ModelForm):
    """Form for adding/editing order items with validation."""
    
    class Meta:
        model = OrderItem
        fields = ['cloth_type', 'quantity', 'special_instructions']
        widgets = {
            'cloth_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'quantity': forms.NumberInput({
                'class': 'form-control',
                'min': 1,
            }),
            'special_instructions': forms.Textarea({
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Any special instructions for this item...',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Get active cloth types and order them by name
        cloth_type_queryset = ClothType.objects.filter(is_active=True).order_by('name')
        
        # Set the queryset for the cloth_type field
        self.fields['cloth_type'].queryset = cloth_type_queryset
        self.fields['quantity'].initial = 1
        
        # Set required attributes
        self.fields['cloth_type'].required = True
        self.fields['quantity'].required = True
        
        # Set widget attributes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = f'form-control {field_name}'
            if field.required:
                field.widget.attrs['class'] += ' required'
            
        # Special handling for cloth_type
        self.fields['cloth_type'].widget.attrs.update({
            'class': 'form-select cloth-type-select',
            'data-live-search': 'true',
        })
    
    def clean(self):
        """Validate the form data."""
        cleaned_data = super().clean()
        
        # Check if this is a form that should be deleted
        if self.instance and self.instance.pk and self.cleaned_data.get('DELETE'):
            return cleaned_data
            
        # Check if this is a new form that should be skipped
        if not any(cleaned_data.values()):
            # This is an empty form, skip validation
            return cleaned_data
            
        # Validate cloth_type
        cloth_type = cleaned_data.get('cloth_type')
        if not cloth_type:
            self.add_error('cloth_type', 'Please select a cloth type.')
        elif not cloth_type.is_active:
            raise forms.ValidationError("This cloth type is not available.")
        return cloth_type
    
    def clean_quantity(self):
        """Ensure quantity is at least 1."""
        quantity = self.cleaned_data.get('quantity', 1)
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity
    
    def clean(self):
        """Perform cross-field validation."""
        cleaned_data = super().clean()
        
        # Skip further validation if we already have errors
        if any(field in self.errors for field in cleaned_data):
            return cleaned_data
            
        # Ensure we have a valid cloth_type
        cloth_type = cleaned_data.get('cloth_type')
        if not cloth_type:
            self.add_error('cloth_type', 'Please select a cloth type.')
            return cleaned_data
            
        # Set default quantity if not provided
        if 'quantity' not in cleaned_data:
            cleaned_data['quantity'] = 1
            
        # Calculate total price if we have both required fields
        if cloth_type and 'quantity' in cleaned_data:
            cleaned_data['unit_price'] = cloth_type.price_per_unit
            cleaned_data['total_price'] = (
                cleaned_data['unit_price'] * cleaned_data['quantity']
            )
            
        return cleaned_data

class BaseOrderItemFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False

def get_order_item_formset(user=None, *args, **kwargs):
    """
    Returns an OrderItemFormSet with the given user.
    This is a factory function to create formsets with user context.
    """
    FormSet = inlineformset_factory(
        Order,
        OrderItem,
        form=OrderItemForm,
        formset=BaseOrderItemFormSet,
        extra=1,
        can_delete=True,
        can_delete_extra=True
    )
    
    # Create a formset class with the user
    class UserFormSet(FormSet):
        def __init__(self, *args, **kwargs):
            # Get the user from kwargs if it exists
            self.user = kwargs.pop('user', user)
            super().__init__(*args, **kwargs)
        
        def _construct_form(self, i, **kwargs):
            # Pass the user to each form in the formset
            kwargs['user'] = self.user
            return super()._construct_form(i, **kwargs)
    
    return UserFormSet(*args, **kwargs)

# Create a default formset factory for direct imports
OrderItemFormSet = get_order_item_formset()
