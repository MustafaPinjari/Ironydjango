"""
URL configuration for the accounts app.
"""
from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from allauth.account.views import (
    LoginView, LogoutView, SignupView, PasswordChangeView,
    PasswordSetView, PasswordResetView, PasswordResetDoneView,
    PasswordResetFromKeyView, PasswordResetFromKeyDoneView,
    EmailVerificationSentView, ConfirmEmailView, EmailView
)
from . import views
from .views_custom import CustomSignupView

app_name = 'accounts'

urlpatterns = [
    # Custom profile URLs (protected by login_required)
    path('profile/', login_required(views.ProfileView.as_view()), name='profile'),
    path('profile/edit/', login_required(views.ProfileEditView.as_view()), name='profile_edit'),
    
    # Allauth overrides (custom templates)
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='account_login'),
    path('signup/', CustomSignupView.as_view(template_name='account/signup.html'), name='account_signup'),
    path('logout/', LogoutView.as_view(template_name='accounts/logout.html'), name='account_logout'),
    
    # Password management
    path('password/change/', 
        login_required(PasswordChangeView.as_view(template_name='accounts/password_change.html')), 
        name='account_change_password'
    ),
    path('password/set/', 
        login_required(PasswordSetView.as_view(template_name='accounts/password_set.html')), 
        name='account_set_password'
    ),
    
    # Email management
    path('email/', 
        login_required(EmailView.as_view(template_name='accounts/email.html')), 
        name='account_email'
    ),
    path('confirm-email/', 
        EmailVerificationSentView.as_view(template_name='accounts/verification_sent.html'), 
        name='account_email_verification_sent'
    ),
    path('confirm-email/<str:key>/', 
        ConfirmEmailView.as_view(), 
        name='account_confirm_email'
    ),
    
    # Password reset
    path('password/reset/', 
        PasswordResetView.as_view(template_name='accounts/password_reset.html'), 
        name='account_reset_password'
    ),
    path('password/reset/done/', 
        PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
        name='account_reset_password_done'
    ),
    path('password/reset/key/<str:uidb36>/<str:key>/', 
        PasswordResetFromKeyView.as_view(template_name='accounts/password_reset_from_key.html'), 
        name='account_reset_password_from_key'
    ),
    path('password/reset/key/done/', 
        PasswordResetFromKeyDoneView.as_view(template_name='accounts/password_reset_from_key_done.html'), 
        name='account_reset_password_from_key_done'
    ),
]
