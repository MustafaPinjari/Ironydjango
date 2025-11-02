"""
URL configuration for the orders app.
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('create/', views.OrderCreateView.as_view(), name='create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.OrderUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.OrderDeleteView.as_view(), name='delete'),
]
