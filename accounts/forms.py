"""
Forms for the accounts app.
"""
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm as BasePasswordChangeForm,
)
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

from .models import User

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label=_('First Name'),
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label=_('Last Name'),
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        label=_('Phone Number'),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Role choices
    ROLE_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('PRESS', 'Press Person'),
        ('DELIVERY', 'Delivery Partner')
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='CUSTOMER',
        label=_('I am a')
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update widget attributes for password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Set help text for password fields
        self.fields['password1'].help_text = _(
            "Your password must contain at least 8 characters, including at least one letter and one number."
        )
        self.fields['password2'].help_text = _("Enter the same password as before, for verification.")


class UserProfileForm(forms.ModelForm):
    """Form for user profile viewing and editing."""
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': True}),
        required=False
    )
    first_name = forms.CharField(
        label=_('First Name'),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    last_name = forms.CharField(
        label=_('Last Name'),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    phone_number = forms.CharField(
        label=_('Phone Number'),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].help_text = None
        
        # Define role choices
        role_choices = [
            ('CUSTOMER', 'Customer'),
            ('PRESS', 'Press Person'),
            ('DELIVERY', 'Delivery Partner')
        ]
        
        # Set role choices for the field
        self.fields['role'].choices = role_choices
        
        # Set default role if not already set
        if not self.initial.get('role'):
            self.initial['role'] = 'CUSTOMER'
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if hasattr(user, 'userprofile'):
            profile = user.userprofile
            if 'profile_picture' in self.cleaned_data:
                profile.profile_picture = self.cleaned_data['profile_picture']
            if 'address' in self.cleaned_data:
                profile.address = self.cleaned_data['address']
            profile.save()
        return user


class UserProfileEditForm(forms.ModelForm):
    """Form for editing user profile."""
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': True}),
        required=False
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add fields from UserProfile
        if hasattr(self.instance, 'userprofile'):
            profile = self.instance.userprofile
            self.fields['profile_picture'] = forms.ImageField(
                label=_('Profile Picture'),
                required=False,
                widget=forms.FileInput(attrs={'class': 'form-control'}),
                initial=profile.profile_picture
            )
            self.fields['address'] = forms.CharField(
                label=_('Address'),
                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                required=False,
                initial=profile.address
            )
            
            # Add clear checkbox for the profile picture
            self.fields['profile_picture'].widget.clear_checkbox_label = _('Remove')
            self.fields['profile_picture'].widget.template_name = 'widgets/clearable_file_input.html'
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if hasattr(user, 'userprofile') and commit:
            profile = user.userprofile
            if 'profile_picture' in self.cleaned_data:
                profile.profile_picture = self.cleaned_data['profile_picture']
            if 'address' in self.cleaned_data:
                profile.address = self.cleaned_data['address']
            profile.save()
        return user


class UserPasswordChangeForm(BasePasswordChangeForm):
    """Form for changing user password."""
    old_password = forms.CharField(
        label=_('Current Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Enter current password')}),
        strip=False,
    )
    
    new_password1 = forms.CharField(
        label=_('New Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Enter new password')}),
        strip=False,
        help_text=_(
            'Your password must contain at least 8 characters, including at least one letter and one number.'
        ),
    )
    
    new_password2 = forms.CharField(
        label=_('New Password Confirmation'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Confirm new password')}),
        strip=False,
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = _(
            'Your password must contain at least 8 characters, including at least one letter and one number.'
        )


class UserAdminForm(forms.ModelForm):
    """Form for admin to create/edit users."""
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text=_('Leave blank if not changing the password.')
    )
    
    password2 = forms.CharField(
        label=_('Password Confirmation'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text=_('Enter the same password as above, for verification.')
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'role', 'is_active', 'is_staff', 'is_superuser')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        """Validate that the two password entries match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password1 != password2:
            self.add_error('password2', _("The two password fields didn't match."))
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save the user with the given password."""
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        
        return user
