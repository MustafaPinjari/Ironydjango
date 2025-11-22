from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views_dashboards import CustomerDashboardView, PressDashboardView, DeliveryDashboardView, AdminDashboardView
from .views_status import UpdateOrderStatusView
from .views import AcceptOrderView, SchedulePickupView

app_name = 'orders'  # This sets the application namespace

urlpatterns = [
    # Dashboard views
    path('dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('dashboard/press/', PressDashboardView.as_view(), name='press_dashboard'),
    path('dashboard/delivery/', DeliveryDashboardView.as_view(), name='delivery_dashboard'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # Order creation and listing
    path('', views.OrderListView.as_view(), name='list'),
    path('create/', views.OrderCreateView.as_view(), name='create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.OrderUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.OrderDeleteView.as_view(), name='delete'),
    
    # Status management
    path('<int:pk>/update-status/', UpdateOrderStatusView.as_view(), name='update_status'),
    path('<int:order_id>/request-cancellation/', views.RequestCancellationView.as_view(), 
         name='request_cancellation'),
    
    # Staff assignment
    path('<int:order_id>/assign-staff/', views.AssignStaffView.as_view(), name='assign_staff'),
    path('<int:order_id>/assign-delivery/', views.AssignDeliveryView.as_view(), name='assign_delivery'),
    
    # Order confirmation
    path('<int:pk>/confirmation/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    
    # Order acceptance and scheduling
    path('<int:pk>/accept/', AcceptOrderView.as_view(), name='accept_order'),
    path('<int:pk>/schedule-pickup/', SchedulePickupView.as_view(), name='schedule_pickup'),
    path('<int:pk>/cancel/', views.CancelOrderView.as_view(), name='cancel'),
    
    # Role-based views (kept for backward compatibility)
    path('assigned/', views.AssignedOrdersView.as_view(), name='assigned'),
    path('press/', views.PressOrderListView.as_view(), name='press_list'),
    path('delivery/', views.DeliveryOrderListView.as_view(), name='delivery_list'),
]
