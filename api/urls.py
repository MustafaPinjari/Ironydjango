"""
URL configuration for the API app.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

# Create a router and register our viewsets with it.
router = DefaultRouter()
# router.register('some-resource', views.SomeViewSet)

urlpatterns = [
    # API endpoints will be added here
] + router.urls

# Only serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)