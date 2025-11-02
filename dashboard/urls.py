"""
URL configuration for the dashboard app.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]
