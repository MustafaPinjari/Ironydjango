"""
Custom views for the accounts app that extend Allauth's views.
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from allauth.account.views import SignupView as AllauthSignupView
from allauth.account.utils import complete_signup
from allauth.account import app_settings

from .forms import UserRegistrationForm

class CustomSignupView(AllauthSignupView):
    """
    Custom signup view that extends Allauth's SignupView to handle role selection.
    """
    form_class = UserRegistrationForm
    template_name = 'account/signup.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs
    
    def form_valid(self, form):
        # Create the user but don't log them in yet
        self.user = form.save(self.request)
        
        # Get the selected role from the form
        role = form.cleaned_data.get('role')
        
        # Set the user's role
        self.user.role = role
        self.user.save()
        
        # Complete the signup (sends confirmation email, etc.)
        return complete_signup(
            self.request, 
            self.user,
            app_settings.EMAIL_VERIFICATION,
            self.get_success_url(),
        )
    
    def get_success_url(self):
        """
        Redirect users based on their role after signup.
        """
        # Get the redirect URL from the form or use the default
        redirect_to = self.request.POST.get('next', '')
        
        # If there's a specific redirect URL, use it
        if redirect_to:
            return redirect_to
            
        # Otherwise, redirect based on role
        if self.user.role == self.user.Role.CUSTOMER:
            return reverse('dashboard:home')
        elif self.user.role == self.user.Role.PRESS:
            return reverse('press:dashboard')
        elif self.user.role == self.user.Role.DELIVERY:
            return reverse('delivery:dashboard')
        elif self.user.role == self.user.Role.ADMIN:
            return reverse('admin:index')
            
        # Default fallback
        return reverse('home')
