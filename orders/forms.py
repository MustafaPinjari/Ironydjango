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
            'notes'
        ]
        widgets = {
            'pickup_date': DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'delivery_date': DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'pickup_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'delivery_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Any special instructions...'}),
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
    class Meta:
        model = OrderItem
        fields = ['cloth_type', 'quantity', 'special_instructions']
        widgets = {
            'cloth_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'special_instructions': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cloth_type'].queryset = ClothType.objects.filter(is_active=True)
        self.fields['quantity'].initial = 1

# Create a formset for order items
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=False,
    min_num=1,
    validate_min=True
)
