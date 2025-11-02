"""
Views for the accounts app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import View, UpdateView, TemplateView, DetailView
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.conf import settings

# Third-party imports
from allauth.account.views import (
    SignupView as AllauthSignupView,
    LoginView as AllauthLoginView,
    PasswordChangeView as AllauthPasswordChangeView,
    PasswordSetView as AllauthPasswordSetView,
    EmailView as AllauthEmailView,
)
from allauth.account.internal.flows.email_verification import send_verification_email_for_user
from allauth.account.models import EmailAddress

# Local imports
from .models import User, UserProfile
from .forms import (
    UserProfileEditForm,
    UserProfileForm,
    UserPasswordChangeForm,
)

# Get the User model
User = get_user_model()


class CustomSignupView(AllauthSignupView):
    """Custom signup view that extends Allauth's SignupView."""
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('dashboard:home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Create an Account')
        return context
    
    def form_valid(self, form):
        """
        Override form_valid to add custom logic after user is created.
        """
        # Call the parent's form_valid method which creates the user
        response = super().form_valid(form)
        
        # Add welcome message
        messages.success(
            self.request,
            _('Registration successful! Welcome to Ironyy.')
        )
        
        # Create user profile
        UserProfile.objects.get_or_create(user=self.user)
        
        return response


class ProfileView(LoginRequiredMixin, DetailView):
    """View for displaying user profile."""
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'user_profile'
    
    def get_object(self, queryset=None):
        """Return the user's own profile."""
        return self.request.user
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context.update({
            'title': _('My Profile'),
            'profile': user.userprofile,
            'orders': user.orders.all()[:5],  # Recent orders
            'unread_notifications': user.notifications.unread().count(),
        })
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """View for editing user profile."""
    model = User
    form_class = UserProfileEditForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        """Return the user's own profile."""
        return self.request.user
    
    def get_form_kwargs(self):
        """Pass the request to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': _('Edit Profile'),
            'profile_form': UserProfileForm(
                instance=self.request.user.userprofile,
                prefix='profile'
            )
        })
        return context
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Handle POST requests with profile and user forms."""
        self.object = self.get_object()
        form = self.get_form()
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user.userprofile,
            prefix='profile'
        )
        
        if form.is_valid() and profile_form.is_valid():
            return self.form_valid(form, profile_form)
        else:
            return self.form_invalid(form, profile_form)
    
    def form_valid(self, form, profile_form):
        """If all forms are valid, save the associated models."""
        self.object = form.save()
        profile_form.save()
        
        messages.success(
            self.request,
            _('Your profile has been updated successfully.')
        )
        
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form, profile_form):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(
            self.get_context_data(form=form, profile_form=profile_form)
        )


class CustomPasswordChangeView(AllauthPasswordChangeView):
    """Custom password change view that extends Allauth's view."""
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Change Password')
        return context
    
    def form_valid(self, form):
        """Add success message and update session auth hash."""
        response = super().form_valid(form)
        update_session_auth_hash(self.request, self.request.user)
        messages.success(
            self.request,
            _('Your password has been changed successfully.')
        )
        return response


class RoleRequiredMixin(UserPassesTestMixin):
    """
    Mixin to check if user has the required role.
    """
    required_roles = []
    permission_denied_message = _('You do not have permission to access this page.')
    
    def test_func(self):
        """Check if the user has the required role."""
        user = self.request.user
        
        if not user.is_authenticated:
            return False
        
        # Superusers can access anything
        if user.is_superuser:
            return True
            
        # If no roles specified, any authenticated user can access
        if not self.required_roles:
            return True
            
        # Check if user has any of the required roles
        return user.role in self.required_roles
    
    def handle_no_permission(self):
        """
        Handle failed permission check.
        """
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
            
        messages.error(self.request, self.get_permission_denied_message())
        
        if self.request.user.is_authenticated:
            return redirect('dashboard:home')
        else:
            return redirect('account_login')


class CustomerRequiredMixin(RoleRequiredMixin):
    """Mixin to check if user is a customer."""
    required_roles = [User.Role.CUSTOMER]
    permission_denied_message = _('This page is only accessible to customers.')


class PressPersonRequiredMixin(RoleRequiredMixin):
    """Mixin to check if user is a press person."""
    required_roles = [User.Role.PRESS]
    permission_denied_message = _('This page is only accessible to press personnel.')


class DeliveryPersonRequiredMixin(RoleRequiredMixin):
    """Mixin to check if user is a delivery person."""
    required_roles = [User.Role.DELIVERY]
    permission_denied_message = _('This page is only accessible to delivery personnel.')


class AdminRequiredMixin(RoleRequiredMixin):
    """Mixin to check if user is an admin or superuser."""
    required_roles = [User.Role.ADMIN]
    permission_denied_message = _('This page is only accessible to administrators.')
    
    def test_func(self):
        """Check if the user is an admin or superuser."""
        user = self.request.user
        return user.is_authenticated and (user.role == User.Role.ADMIN or user.is_superuser)


class StaffRequiredMixin(RoleRequiredMixin):
    """Mixin to check if user is staff (admin, press, or delivery)."""
    required_roles = [User.Role.ADMIN, User.Role.PRESS, User.Role.DELIVERY]
    permission_denied_message = _('This page is only accessible to staff members.')


# Additional views for account management
class AccountInactiveView(TemplateView):
    """View shown when account is inactive."""
    template_name = 'account/account_inactive.html'


class EmailVerificationSentView(TemplateView):
    """View shown after sending email verification."""
    template_name = 'account/verification_sent.html'


@method_decorator(login_required, name='dispatch')
class EmailVerificationView(View):
    """View for handling email verification."""
    def get(self, request, *args, **kwargs):
        """Resend verification email."""
        email = request.user.email
        email_address = EmailAddress.objects.get_for_user(request.user, email)
        
        if not email_address.verified:
            send_verification_email_for_user(request, request.user)
            messages.success(
                request,
                _('Verification email has been resent. Please check your inbox.')
            )
        else:
            messages.info(request, _('Your email is already verified.'))
        
        return redirect('account_email')
