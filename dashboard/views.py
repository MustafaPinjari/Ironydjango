from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, DetailView, UpdateView
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q

from orders.models import Order, OrderItem
from accounts.models import User

class RoleBasedDashboardView(LoginRequiredMixin, View):
    """
    Base view that redirects users to their role-specific dashboard.
    """
    def get(self, request, *args, **kwargs):
        if request.user.is_admin:
            return redirect('dashboard:admin_dashboard')
        elif request.user.is_press:
            return redirect('dashboard:press_dashboard')
        elif request.user.is_delivery:
            return redirect('dashboard:delivery_dashboard')
        return redirect('dashboard:customer_dashboard')

class CustomerDashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard for customers to view their orders.
    """
    model = Order
    template_name = 'dashboard/customer_dashboard.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_orders = Order.objects.filter(customer=self.request.user)
        
        context['active_orders_count'] = user_orders.exclude(
            status__in=[Order.Status.COMPLETED, Order.Status.CANCELLED, Order.Status.REFUNDED]
        ).count()
        
        from django.db.models import Sum
        total_spent = user_orders.filter(
            status=Order.Status.COMPLETED
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        context['total_spent'] = total_spent
        return context

class PressDashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard for press staff to manage orders.
    """
    model = Order
    template_name = 'dashboard/press_dashboard.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        # Show orders relevant to press staff
        return Order.objects.filter(
            Q(status=Order.Status.CONFIRMED) |  # New orders to accept
            Q(status=Order.Status.PICKED_UP) |  # Arrived at press
            Q(status=Order.Status.PROCESSING) | # In progress
            Q(status=Order.Status.READY)        # Done, waiting for delivery
        ).order_by('status', 'created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['pending_requests_count'] = Order.objects.filter(status=Order.Status.CONFIRMED).count()
        context['in_progress_count'] = Order.objects.filter(status=Order.Status.PROCESSING).count()
        context['ready_count'] = Order.objects.filter(status=Order.Status.READY).count()
        
        return context

class DeliveryDashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard for delivery partners to manage pickups and deliveries.
    """
    model = Order
    template_name = 'dashboard/delivery_dashboard.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        # Show orders relevant to delivery partners
        # 1. Orders available for pickup (SCHEDULED_FOR_PICKUP) - Show to all or just assigned? 
        #    Let's assume initially show to all, or if assigned show to assigned.
        # 2. Orders ready for delivery (READY)
        # 3. My active tasks (OUT_FOR_PICKUP, OUT_FOR_DELIVERY)
        
        user = self.request.user
        return Order.objects.filter(
            Q(status=Order.Status.SCHEDULED_FOR_PICKUP) |  # Available for pickup
            Q(status=Order.Status.READY) |                 # Available for delivery
            Q(delivery_person=user, status__in=[          # My active tasks
                Order.Status.OUT_FOR_PICKUP,
                Order.Status.OUT_FOR_DELIVERY
            ])
        ).order_by('status', 'created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['available_pickups_count'] = Order.objects.filter(status=Order.Status.SCHEDULED_FOR_PICKUP).count()
        context['active_pickups_count'] = Order.objects.filter(delivery_person=user, status=Order.Status.OUT_FOR_PICKUP).count()
        context['available_deliveries_count'] = Order.objects.filter(status=Order.Status.READY).count()
        context['active_deliveries_count'] = Order.objects.filter(delivery_person=user, status=Order.Status.OUT_FOR_DELIVERY).count()
        
        return context

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Admin dashboard with system overview and management options.
    """
    model = Order
    template_name = 'dashboard/admin_dashboard.html'
    context_object_name = 'recent_orders'
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_queryset(self):
        return Order.objects.all().order_by('-created_at')[:10]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_orders'] = Order.objects.filter(status=Order.Status.PENDING).count()
        context['in_progress_orders'] = Order.objects.filter(
            status__in=[Order.Status.PROCESSING, Order.Status.PICKED_UP]
        ).count()
        context['delivery_pending'] = Order.objects.filter(
            status__in=[Order.Status.SCHEDULED_FOR_PICKUP, Order.Status.READY]
        ).count()
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    View order details with role-based access control.
    """
    model = Order
    template_name = 'dashboard/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        # Customers can only see their own orders
        if user.is_customer:
            return qs.filter(customer=user)
        # Press staff can see all orders
        elif user.is_press or user.is_admin:
            return qs
        # Delivery partners can only see their assigned orders
        elif user.is_delivery:
            return qs.filter(delivery_person=user)
        return qs.none()

class UpdateOrderStatusView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    View for updating order status (for press staff and delivery partners).
    """
    model = Order
    template_name = 'dashboard/update_order_status.html'
    context_object_name = 'order'
    
    def test_func(self):
        user = self.request.user
        if user.is_admin:
            return True
        
        order = self.get_object()
        # Allow customers to confirm their own draft/pending orders
        if user.is_customer and order.customer == user:
            return order.status in [Order.Status.DRAFT, Order.Status.PENDING]
            
        if user.is_press:
            return order.assigned_staff == user or order.assigned_staff is None
        elif user.is_delivery:
            return order.delivery_person == user or (
                order.status == Order.Status.SCHEDULED_FOR_PICKUP and order.delivery_person is None
            )
        return False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        
        # Get valid transitions for current status
        valid_transitions = {
            Order.Status.DRAFT: [Order.Status.CONFIRMED, Order.Status.CANCELLED],
            Order.Status.PENDING: [Order.Status.CONFIRMED, Order.Status.CANCELLED],
            Order.Status.CONFIRMED: [Order.Status.SCHEDULED_FOR_PICKUP, Order.Status.CANCELLED],
            Order.Status.SCHEDULED_FOR_PICKUP: [Order.Status.OUT_FOR_PICKUP, Order.Status.CANCELLED],
            Order.Status.OUT_FOR_PICKUP: [Order.Status.PICKED_UP, Order.Status.CANCELLED],
            Order.Status.PICKED_UP: [Order.Status.PROCESSING, Order.Status.CANCELLED],
            Order.Status.PROCESSING: [Order.Status.READY, Order.Status.CANCELLED],
            Order.Status.READY: [Order.Status.OUT_FOR_DELIVERY, Order.Status.CANCELLED],
            Order.Status.OUT_FOR_DELIVERY: [Order.Status.COMPLETED, Order.Status.CANCELLED],
        }
        
        # Get valid next statuses
        valid_next_statuses = valid_transitions.get(order.status, [])
        
        # Create choices for the status dropdown
        status_choices = [(status, Order.Status(status).label) for status in valid_next_statuses]
        
        # Get staff and delivery partner choices
        from accounts.models import User
        press_staff = User.objects.filter(role=User.Role.PRESS)
        delivery_partners = User.objects.filter(role=User.Role.DELIVERY)
        
        context['status_choices'] = status_choices
        context['press_staff'] = press_staff
        context['delivery_partners'] = delivery_partners
        context['all_statuses'] = Order.Status.choices
        
        return context
    
    def post(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.POST.get('status')
        
        # Validate status transition
        valid_transitions = {
            Order.Status.DRAFT: [Order.Status.CONFIRMED, Order.Status.CANCELLED],
            Order.Status.PENDING: [Order.Status.CONFIRMED, Order.Status.CANCELLED],
            Order.Status.CONFIRMED: [Order.Status.SCHEDULED_FOR_PICKUP, Order.Status.CANCELLED],
            Order.Status.SCHEDULED_FOR_PICKUP: [Order.Status.OUT_FOR_PICKUP, Order.Status.CANCELLED],
            Order.Status.OUT_FOR_PICKUP: [Order.Status.PICKED_UP, Order.Status.CANCELLED],
            Order.Status.PICKED_UP: [Order.Status.PROCESSING, Order.Status.CANCELLED],
            Order.Status.PROCESSING: [Order.Status.READY, Order.Status.CANCELLED],
            Order.Status.READY: [Order.Status.OUT_FOR_DELIVERY, Order.Status.CANCELLED],
            Order.Status.OUT_FOR_DELIVERY: [Order.Status.COMPLETED, Order.Status.CANCELLED],
        }
        
        transitions = valid_transitions.get(order.status, [])
        
        if new_status in transitions:
            order.status = new_status
            # Assign staff if needed
            if new_status == Order.Status.SCHEDULED_FOR_PICKUP and request.user.is_press:
                order.assigned_staff = request.user
            elif new_status == Order.Status.OUT_FOR_PICKUP and request.user.is_delivery:
                order.delivery_person = request.user
                
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}')
        else:
            messages.error(request, 'Invalid status transition')
        
        return redirect('dashboard:order_detail', pk=order.pk)

