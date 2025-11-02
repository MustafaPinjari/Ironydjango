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


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration.
    """
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Enter your email')}),
        help_text=_('Required. Enter a valid email address.')
    )
    
    first_name = forms.CharField(
        label=_('First Name'),
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter your first name')}),
        required=True
    )
    
    last_name = forms.CharField(
        label=_('Last Name'),
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter your last name')}),
        required=True
    )
    
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Create a password')}),
        help_text=_(
            'Your password must contain at least 8 characters, including at least one letter and one number.'
        )
    )
    
    password2 = forms.CharField(
        label=_('Password Confirmation'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Confirm your password')}),
        help_text=_('Enter the same password as before, for verification.')
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    
    phone_number = forms.CharField(
        label=_('Phone Number'),
        validators=[phone_regex],
        max_length=17,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('e.g., +1234567890')
        }),
        required=False
    )
    
    role = forms.ChoiceField(
        label=_('I am a'),
        choices=User.Role.choices,
        initial=User.Role.CUSTOMER,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        help_text=_('Select your role in the system.')
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'role')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the default help text for username
        self.fields['email'].help_text = None
        
        # Set role choices based on user type (for admin adding users)
        if 'initial' in kwargs and 'role' in kwargs['initial']:
            self.fields['role'].initial = kwargs['initial']['role']
    
    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))
        return email


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
        # If the user has a profile, get the initial data
        if hasattr(self.instance, 'userprofile'):
            profile = self.instance.userprofile
            self.fields['profile_picture'] = forms.ImageField(
                label=_('Profile Picture'),
                required=False,
                widget=forms.FileInput(attrs={'class': 'form-control'})
            )
            self.fields['address'] = forms.CharField(
                label=_('Address'),
                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                required=False,
                initial=profile.address
            )
            if profile.profile_picture:
                self.fields['profile_picture'].initial = profile.profile_picture
    
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
