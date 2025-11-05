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

class PressDashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard for press staff to manage orders.
    """
    model = Order
    template_name = 'dashboard/press_dashboard.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        # Show all pending and in-progress orders
        return Order.objects.filter(
            Q(status=Order.Status.PENDING) | 
            Q(status=Order.Status.CONFIRMED) |
            Q(status=Order.Status.IN_PROGRESS) |
            Q(status=Order.Status.READY_FOR_PICKUP)
        ).order_by('status', 'pickup_date')

class DeliveryDashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard for delivery partners to manage pickups and deliveries.
    """
    model = Order
    template_name = 'dashboard/delivery_dashboard.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        # Show only orders assigned to this delivery partner
        return Order.objects.filter(
            delivery_partner=self.request.user,
            status__in=[
                Order.Status.READY_FOR_PICKUP,
                Order.Status.PICKED_UP
            ]
        ).order_by('scheduled_delivery')

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
            status__in=[Order.Status.CONFIRMED, Order.Status.IN_PROGRESS]
        ).count()
        context['delivery_pending'] = Order.objects.filter(
            status=Order.Status.READY_FOR_PICKUP
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
            return qs.filter(delivery_partner=user)
        return qs.none()

class UpdateOrderStatusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View for updating order status (for press staff and delivery partners).
    """
    model = Order
    fields = []  # We'll handle the status update in form_valid
    template_name = 'dashboard/update_order_status.html'
    
    def test_func(self):
        user = self.request.user
        if user.is_admin:
            return True
        
        order = self.get_object()
        if user.is_press:
            return order.press_person == user or order.press_person is None
        elif user.is_delivery:
            return order.delivery_partner == user
        return False
    
    def form_valid(self, form):
        new_status = self.request.POST.get('status')
        order = self.get_object()
        
        # Validate status transition
        valid_transitions = {
            'PENDING': ['CONFIRMED', 'REJECTED'],
            'CONFIRMED': ['IN_PROGRESS', 'CANCELLED'],
            'IN_PROGRESS': ['READY_FOR_PICKUP', 'CANCELLED'],
            'READY_FOR_PICKUP': ['PICKED_UP', 'CANCELLED'],
            'PICKED_UP': ['DELIVERED', 'CANCELLED'],
        }
        
        if new_status in valid_transitions.get(order.status, []):
            order.status = new_status
            order.save()
            messages.success(self.request, f'Order status updated to {order.get_status_display()}')
        else:
            messages.error(self.request, 'Invalid status transition')
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('dashboard:order_detail', kwargs={'pk': self.object.pk})
