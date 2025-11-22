from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.utils import timezone

from .models import Order

class CustomerDashboardView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/customer_dashboard.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Order.objects.filter(customer=self.request.user)
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            if status == 'pending':
                queryset = queryset.filter(status__in=['pending', 'confirmed', 'processing'])
            elif status == 'in_progress':
                queryset = queryset.filter(status__in=['processing', 'ready', 'out_for_delivery'])
            elif status == 'ready':
                queryset = queryset.filter(status='ready')
            elif status == 'completed':
                queryset = queryset.filter(status__in=['completed', 'cancelled', 'refunded'])
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'dashboard'
        return context


class PressDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'orders/press_dashboard.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.role in ['PRESS', 'ADMIN']
    
    def get_queryset(self):
        queryset = Order.objects.filter(assigned_staff=self.request.user)
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            if status == 'assigned':
                queryset = queryset.filter(status='assigned')
            elif status == 'in_progress':
                queryset = queryset.filter(status='processing')
            elif status == 'ready':
                queryset = queryset.filter(status='ready')
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get counts for the dashboard cards
        context.update({
            'assigned_count': Order.objects.filter(
                assigned_staff=user, 
                status='assigned'
            ).count(),
            'in_progress_count': Order.objects.filter(
                assigned_staff=user, 
                status='processing'
            ).count(),
            'ready_count': Order.objects.filter(
                assigned_staff=user, 
                status='ready'
            ).count(),
            'completed_count': Order.objects.filter(
                assigned_staff=user, 
                status='completed'
            ).count(),
            'active_tab': 'press_dashboard',
        })
        return context


class DeliveryDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'orders/delivery_dashboard.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.role in ['DELIVERY', 'ADMIN']
    
    def get_queryset(self):
        # For delivery staff, show orders that are ready for delivery or assigned to them
        queryset = Order.objects.filter(
            Q(status='ready', delivery_type='delivery') | 
            Q(delivery_person=self.request.user, status='out_for_delivery')
        )
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status == 'ready':
            queryset = queryset.filter(status='ready')
        elif status == 'out_for_delivery':
            queryset = queryset.filter(status='out_for_delivery')
        elif status == 'delivered':
            queryset = Order.objects.filter(
                delivery_person=self.request.user,
                status='completed'
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get counts for the dashboard cards
        context.update({
            'assigned_count': Order.objects.filter(
                delivery_person=user, 
                status='out_for_delivery'
            ).count(),
            'out_for_delivery_count': Order.objects.filter(
                delivery_person=user, 
                status='out_for_delivery'
            ).count(),
            'delivered_count': Order.objects.filter(
                delivery_person=user, 
                status='completed',
                delivery_type='delivery'
            ).count(),
            'total_count': Order.objects.filter(
                delivery_person=user
            ).count(),
            'active_tab': 'delivery_dashboard',
        })
        return context


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'orders/admin_dashboard.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.role == 'ADMIN'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get counts for different order statuses
        status_counts = Order.objects.values('status').annotate(count=Count('status'))
        status_data = {item['status']: item['count'] for item in status_counts}
        
        # Get recent orders
        recent_orders = Order.objects.select_related('customer', 'assigned_staff', 'delivery_person')\
                                   .order_by('-created_at')[:10]
        
        # Get staff performance metrics (top 5)
        from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
        from datetime import timedelta
        
        staff_performance = Order.objects.filter(
            status='completed',
            completed_at__isnull=False,
            assigned_staff__isnull=False
        ).annotate(
            processing_time=ExpressionWrapper(
                F('completed_at') - F('created_at'),
                output_field=DurationField()
            )
        ).values(
            'assigned_staff__email',
            'assigned_staff__first_name',
            'assigned_staff__last_name'
        ).annotate(
            total_orders=Count('id'),
            avg_processing_time=Avg('processing_time')
        ).order_by('-total_orders')[:5]
        
        context.update({
            'total_orders': Order.objects.count(),
            'pending_orders': status_data.get('pending', 0) + status_data.get('confirmed', 0),
            'in_progress_orders': status_data.get('processing', 0),
            'ready_orders': status_data.get('ready', 0),
            'completed_orders': status_data.get('completed', 0),
            'recent_orders': recent_orders,
            'staff_performance': staff_performance,
            'active_tab': 'admin_dashboard',
        })
        return context
