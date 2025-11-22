from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from .models import Order, OrderStatusUpdate

class UpdateOrderStatusView(LoginRequiredMixin, View):
    """
    View to handle order status updates with proper permissions and logging.
    """
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '').strip()
        
        # Check if status is valid
        if not new_status or new_status not in dict(Order.Status.choices):
            messages.error(request, _('Invalid status provided.'))
            return redirect('orders:detail', pk=order.pk)
        
        # Check permissions based on user role
        if not self._has_permission(request.user, order, new_status):
            messages.error(request, _('You do not have permission to perform this action.'))
            return redirect('orders:detail', pk=order.pk)
        
        # Update order status
        old_status = order.status
        order.status = new_status
        
        # Update timestamps based on status
        now = timezone.now()
        if new_status == Order.Status.PROCESSING and not order.processing_started_at:
            order.processing_started_at = now
        elif new_status == Order.Status.READY and not order.ready_at:
            order.ready_at = now
        elif new_status == Order.Status.OUT_FOR_DELIVERY and not order.out_for_delivery_at:
            order.out_for_delivery_at = now
        elif new_status == Order.Status.COMPLETED and not order.completed_at:
            order.completed_at = now
        elif new_status == Order.Status.CANCELLED and not order.cancelled_at:
            order.cancelled_at = now
        
        order.save()
        
        # Log the status update
        OrderStatusUpdate.objects.create(
            order=order,
            from_status=old_status,
            to_status=new_status,
            changed_by=request.user,
            notes=notes
        )
        
        # Handle notifications (placeholder for actual notification system)
        self._send_notifications(order, old_status, new_status, request.user)
        
        messages.success(request, _(f'Order status updated to {order.get_status_display()}'))
        
        # Redirect based on user role
        if request.user.role == 'CUSTOMER':
            return redirect('orders:customer_dashboard')
        elif request.user.role == 'PRESS':
            return redirect('orders:press_dashboard')
        elif request.user.role == 'DELIVERY':
            return redirect('orders:delivery_dashboard')
        else:
            return redirect('orders:detail', pk=order.pk)
    
    def _has_permission(self, user, order, new_status):
        """Check if the user has permission to perform the status update."""
        # Admin can do anything
        if user.is_staff or user.role == 'ADMIN':
            return True
            
        # Check based on user role and status transition
        if user.role == 'CUSTOMER':
            # Customers can only cancel their own pending orders
            return (order.customer == user and 
                   new_status == Order.Status.CANCELLED and 
                   order.status in [Order.Status.PENDING, Order.Status.CONFIRMED])
        
        elif user.role == 'PRESS':
            # Press staff can update status for their assigned orders
            return (order.assigned_staff == user and 
                   new_status in [Order.Status.PROCESSING, Order.Status.READY] and
                   order.status in [Order.Status.ASSIGNED, Order.Status.PROCESSING])
        
        elif user.role == 'DELIVERY':
            # Delivery staff can mark orders as out for delivery or delivered
            if new_status == Order.Status.OUT_FOR_DELIVERY:
                return (order.status == Order.Status.READY and 
                       order.delivery_type == Order.DeliveryType.DELIVERY)
            elif new_status == Order.Status.COMPLETED:
                return (order.status == Order.Status.OUT_FOR_DELIVERY and 
                       order.delivery_person == user)
        
        return False
    
    def _send_notifications(self, order, old_status, new_status, changed_by):
        """Send notifications to relevant users about the status change."""
        # This is a placeholder for actual notification logic
        # In a real application, you would integrate with email, SMS, or push notifications
        
        notification_recipients = []
        
        # Notify customer for important status changes
        if new_status in [
            Order.Status.CONFIRMED,
            Order.Status.PROCESSING,
            Order.Status.READY,
            Order.Status.OUT_FOR_DELIVERY,
            Order.Status.COMPLETED,
            Order.Status.CANCELLED
        ]:
            notification_recipients.append(order.customer)
        
        # Notify press staff when order is assigned or requires attention
        if new_status == Order.Status.ASSIGNED and order.assigned_staff:
            notification_recipients.append(order.assigned_staff)
        
        # Notify delivery staff when order is ready for delivery
        if (new_status == Order.Status.READY and 
            order.delivery_type == Order.DeliveryType.DELIVERY and
            order.delivery_person):
            notification_recipients.append(order.delivery_person)
        
        # In a real app, you would send actual notifications here
        # For now, we'll just log to console
        if notification_recipients:
            print(f"\n=== Notification ===")
            print(f"Order #{order.order_number} status changed from {old_status} to {new_status}")
            print(f"Changed by: {changed_by}")
            print(f"Notifying: {', '.join([str(u) for u in notification_recipients])}")
            print("==================\n")
