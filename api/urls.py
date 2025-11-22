"""
URL configuration for the API app.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from orders.api_views import ServiceViewSet

app_name = 'api'

# Create a router and register our viewsets with it.
router = DefaultRouter()

urlpatterns = [
    # Service related endpoints
    path('services/', include([
        path('variants/', ServiceViewSet.as_view({'get': 'variants'}), name='service-variants'),
        path('options/', ServiceViewSet.as_view({'get': 'options'}), name='service-options'),
    ])),
] + router.urls

# Only serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)