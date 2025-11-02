import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, FileExtensionValidator
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse


def user_profile_picture_path(instance, filename):
    """Generate file path for user profile pictures."""
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    return os.path.join('profile_pics', str(instance.user.id), filename)

class UserManager(BaseUserManager):
    """Custom user model manager with email as the unique identifier."""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
            
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Custom user model that uses email as the unique identifier for authentication.
    """
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', _('Customer')
        PRESS = 'PRESS', _('Press Person')
        DELIVERY = 'DELIVERY', _('Delivery Partner')
        ADMIN = 'ADMIN', _('Admin')

    # Remove username field and use email as the unique identifier
    username = None
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _('A user with that email already exists.'),
        },
    )
    
    # Role-based access control
    role = models.CharField(
        _('user role'),
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        help_text=_('Designates the role of the user in the system.')
    )
    
    # Contact information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(
        _('phone number'),
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text=_('Enter a valid phone number (e.g., +1234567890)')
    )
    
    # Account status
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    email_verified = models.BooleanField(
        _('email verified'),
        default=False,
        help_text=_('Designates whether this user has verified their email address.')
    )
    
    # Timestamps
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), blank=True, null=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    # Required fields for AbstractUser
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()

    class Meta(AbstractUser.Meta):
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        swappable = 'AUTH_USER_MODEL'
        permissions = [
            ('view_dashboard', 'Can view dashboard'),
            ('manage_users', 'Can manage users'),
            ('manage_orders', 'Can manage orders'),
        ]

    def __str__(self):
        """Return string representation of the user (full name or email)."""
        full_name = self.get_full_name().strip()
        return full_name if full_name else self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user (first name)."""
        return self.first_name or self.email.split('@')[0]
    
    def get_absolute_url(self):
        """Return the URL to the user's profile page."""
        return reverse('accounts:profile')
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    def send_welcome_email(self):
        """Send a welcome email to the user after registration."""
        subject = _('Welcome to Ironyy Laundry Service')
        html_message = render_to_string('emails/welcome.html', {'user': self})
        plain_message = strip_tags(html_message)
        self.email_user(subject, plain_message, html_message=html_message)
    
    # Role-based properties
    @property
    def is_customer(self):
        """Check if the user has customer role."""
        return self.role == self.Role.CUSTOMER

    @property
    def is_press(self):
        """Check if the user has press person role."""
        return self.role == self.Role.PRESS

    @property
    def is_delivery(self):
        """Check if the user has delivery person role."""
        return self.role == self.Role.DELIVERY

    @property
    def is_admin(self):
        """Check if the user has admin role or is a superuser."""
        return self.role == self.Role.ADMIN or self.is_superuser
    
    @property
    def is_staff_member(self):
        """Check if the user is a staff member (press, delivery, or admin)."""
        return self.role in [self.Role.PRESS, self.Role.DELIVERY, self.Role.ADMIN] or self.is_superuser
    
    # Permissions
    def has_perm(self, perm, obj=None):
        """Check if the user has the specified permission."""
        if self.is_active and self.is_superuser:
            return True
        return super().has_perm(perm, obj)
    
    def has_module_perms(self, app_label):
        """Check if the user has permissions to view the app `app_label`."""
        if self.is_active and self.is_superuser:
            return True
        return super().has_module_perms(app_label)
    
    # Override save to handle role-based permissions
    def save(self, *args, **kwargs):
        # Set is_staff based on role
        self.is_staff = self.is_staff_member
        super().save(*args, **kwargs)
        
        # Add to appropriate group based on role
        if self.role:
            group_name = f"{self.role.lower()}_group"
            group, created = Group.objects.get_or_create(name=group_name)
            self.groups.add(group)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        _('profile picture'),
        upload_to=user_profile_picture_path,
        blank=True,
        null=True
    )
    address = models.TextField(_('address'), blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.email
