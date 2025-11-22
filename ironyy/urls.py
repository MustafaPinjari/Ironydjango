"""
URL configuration for ironyy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Landing page (public)
    path('', views.LandingPageView.as_view(), name='landing'),
    
    # Dashboard (protected routes)
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    
    # Authentication URLs (handled by django-allauth)
    path('accounts/', include('allauth.urls')),
    
    # Custom accounts app URLs
    path('profile/', include('accounts.urls')),
    
    # Orders app
    path('orders/', include('orders.urls', namespace='orders')),
    
    # API endpoints
    path('api/', include('api.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Error handlers
handler400 = 'ironyy.views.handler400'
handler403 = 'ironyy.views.handler403'
handler404 = 'ironyy.views.handler404'
handler500 = 'ironyy.views.handler500'
