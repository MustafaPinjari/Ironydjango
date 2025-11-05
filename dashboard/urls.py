"""
URL configuration for the dashboard app.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard that redirects based on user role
    path('', views.RoleBasedDashboardView.as_view(), name='home'),
    
    # Role-specific dashboards
    path('customer/', views.CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('press/', views.PressDashboardView.as_view(), name='press_dashboard'),
    path('delivery/', views.DeliveryDashboardView.as_view(), name='delivery_dashboard'),
    path('admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # Order management
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('order/<int:pk>/update-status/', views.UpdateOrderStatusView.as_view(), name='update_order_status'),
]
