"""
URL configuration for the orders app.
"""
from django.urls import path
from . import views
from .views import PressOrderListView, DeliveryOrderListView

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('create/', views.OrderCreateView.as_view(), name='create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.OrderUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.OrderDeleteView.as_view(), name='delete'),
    
    # Press staff URLs
    path('press/', PressOrderListView.as_view(), name='press_list'),
    
    # Delivery staff URLs
    path('delivery/', DeliveryOrderListView.as_view(), name='delivery_list'),
]
