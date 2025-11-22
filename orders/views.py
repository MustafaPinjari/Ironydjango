from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import random
import string

from .models import Order, OrderItem, OrderStatusUpdate
from .forms import OrderForm, OrderItemForm, OrderItemFormSet
from accounts.models import User
from services.models import Service, ServiceVariant, ServiceOption

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.role == 'CUSTOMER':
            return Order.objects.filter(customer=self.request.user).order_by('-created_at')
        return Order.objects.all().order_by('-created_at')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        if self.request.user.role == 'CUSTOMER':
            return Order.objects.filter(customer=self.request.user)
        return Order.objects.all()

import logging
from django import forms
from .forms import OrderForm

logger = logging.getLogger(__name__)

# Removed duplicate CancelOrderView - using the one at the bottom of the file

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_create.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = OrderItemFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object,
                form_kwargs={'user': self.request.user}
            )
        else:
            context['formset'] = OrderItemFormSet(
                instance=self.object,
                form_kwargs={'user': self.request.user}
            )
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            with transaction.atomic():
                # Set the customer before saving
                self.object = form.save(commit=False)
                self.object.customer = self.request.user
                self.object.status = Order.Status.CONFIRMED
                self.object.save()
                
                # Save the formset
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.order = self.object
                    instance.save()
                formset.save_m2m()  # Save many-to-many data
                
                # Calculate and save order total
                self.object.calculate_totals()
                
                messages.success(self.request, 'Order created successfully!')
                return super().form_valid(form)
        else:
            # Log formset errors for debugging
            for form in formset:
                if form.errors:
                    logger.warning(f"Formset errors: {form.errors}")
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        if not hasattr(self, 'object') or not self.object or not self.object.pk:
            logger.error("No valid order object found for redirection")
            return reverse_lazy('orders:list')
        return reverse_lazy('orders:detail', kwargs={'pk': self.object.pk})

    def form_invalid(self, form):
        logger.warning(f"Form is invalid. Errors: {form.errors}")
        return super().form_invalid(form)

class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    
    def test_func(self):
        order = self.get_object()
        return self.request.user == order.customer or self.request.user.is_staff
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the user to the form
        kwargs['user'] = self.request.user
        return kwargs
        
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_staff:
            # Remove fields that only staff should edit
            if 'status' in form.fields:
                del form.fields['status']
            if 'payment_status' in form.fields:
                del form.fields['payment_status']
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Order updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('orders:detail', kwargs={'pk': self.object.pk})

class OrderDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:list')
    
    def test_func(self):
        order = self.get_object()
        return self.request.user == order.customer or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Order was successfully cancelled.')
        return super().delete(request, *args, **kwargs)

class AcceptOrderView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View for staff to accept an order and schedule pickup."""
    
    def test_func(self):
        """Only staff members can accept orders."""
        return self.request.user.role in ['PRESS', 'ADMIN']
    
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        
        # Only allow accepting pending or confirmed orders
        if order.status not in [Order.Status.PENDING, Order.Status.CONFIRMED]:
            messages.error(request, 'This order cannot be accepted in its current status.')
            return redirect('orders:press_dashboard')
        
        # Update order status to processing
        previous_status = order.status
        order.status = Order.Status.PROCESSING
        order.assigned_staff = request.user
        order.assigned_at = timezone.now()
        order.save()
        
        # Create status update
        OrderStatusUpdate.objects.create(
            order=order,
            from_status=previous_status,
            to_status=order.status,
            changed_by=request.user,
            notes=f'Order accepted by {request.user.get_full_name() or request.user.email}'
        )
        
        messages.success(request, f'Order #{order.order_number} has been accepted and is now in progress.')
        return redirect('orders:press_dashboard')

class SchedulePickupView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View for staff to schedule a pickup for an order."""
    
    def test_func(self):
        """Only staff members can schedule pickups."""
        return self.request.user.role in ['PRESS', 'ADMIN']
    
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        return render(request, 'orders/schedule_pickup.html', {'order': order})
    
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        
        # Only allow scheduling pickup for processing orders
        if order.status != Order.Status.PROCESSING:
            messages.error(request, 'You can only schedule pickup for orders that are in progress.')
            return redirect('orders:press_dashboard')
        
        pickup_date = request.POST.get('pickup_date')
        pickup_time = request.POST.get('pickup_time')
        notes = request.POST.get('notes', '')
        
        try:
            # Parse the datetime
            from datetime import datetime
            pickup_datetime = datetime.strptime(f"{pickup_date} {pickup_time}", "%Y-%m-%d %H:%M")
            
            # Ensure pickup is in the future
            if pickup_datetime < timezone.now():
                raise ValueError("Pickup time must be in the future.")
                
            # Update order with pickup details
            order.pickup_scheduled_at = pickup_datetime
            order.status = Order.Status.READY
            order.save()
            
            # Create status update
            OrderStatusUpdate.objects.create(
                order=order,
                from_status=Order.Status.PROCESSING,
                to_status=order.status,
                changed_by=request.user,
                notes=f"Pickup scheduled for {pickup_datetime.strftime('%B %d, %Y at %I:%M %p')}. {notes}".strip()
            )
            
            messages.success(request, f'Pickup for order #{order.order_number} has been scheduled successfully.')
            return redirect('orders:press_dashboard')
            
        except ValueError as e:
            messages.error(request, f'Invalid date/time format: {str(e)}')
            return render(request, 'orders/schedule_pickup.html', {'order': order})

class AssignStaffView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Order
    fields = ['assigned_staff']
    template_name = 'orders/assign_staff.html'

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Staff assigned successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('orders:detail', kwargs={'pk': self.object.pk})

class AssignDeliveryView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Order
    fields = ['delivery_person']
    template_name = 'orders/assign_delivery.html'

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Delivery person assigned successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('orders:detail', kwargs={'pk': self.object.pk})

class RequestCancellationView(LoginRequiredMixin, UpdateView):
    model = Order
    fields = []
    template_name = 'orders/request_cancellation.html'

    def form_valid(self, form):
        form.instance.status = Order.Status.CANCELLATION_REQUESTED
        messages.success(self.request, 'Cancellation requested successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('orders:detail', kwargs={'pk': self.object.pk})

class AssignedOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/assigned_orders.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.role == 'PRESS_STAFF':
            return Order.objects.filter(assigned_staff=self.request.user).order_by('-created_at')
        elif self.request.user.role == 'DELIVERY_PERSON':
            return Order.objects.filter(delivery_person=self.request.user).order_by('-created_at')
        return Order.objects.none()

class PressOrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'orders/press_orders.html'
    context_object_name = 'orders'
    paginate_by = 10

    def test_func(self):
        return self.request.user.role in ['PRESS_STAFF', 'ADMIN']

    def get_queryset(self):
        return Order.objects.filter(
            status__in=[Order.Status.PROCESSING, Order.Status.SHIPPED]
        ).order_by('status', 'created_at')

class CancelOrderView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Order
    fields = ['cancellation_reason']
    template_name = 'orders/order_confirm_cancel.html'
    
    def test_func(self):
        order = self.get_object()
        return (self.request.user == order.customer or 
                self.request.user.is_staff or 
                self.request.user == order.assigned_staff or 
                self.request.user == order.delivery_person)
    
    def form_valid(self, form):
        order = form.save(commit=False)
        if order.status != Order.Status.CANCELLED:
            order.status = Order.Status.CANCELLED
            order.cancelled_at = timezone.now()
            order.save(update_fields=['status', 'cancellation_reason', 'cancelled_at', 'updated_at'])
            
            # Create status update
            OrderStatusUpdate.objects.create(
                order=order,
                from_status=order.status,
                to_status=Order.Status.CANCELLED,
                changed_by=self.request.user,
                notes=f'Order cancelled by {self.request.user.get_full_name() or self.request.user.email}. ' \
                     f'Reason: {form.cleaned_data.get("cancellation_reason", "No reason provided")}'
            )
            
            messages.success(self.request, 'Order has been cancelled successfully.')
        else:
            messages.warning(self.request, 'This order is already cancelled.')
            
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('orders:detail', kwargs={'pk': self.object.pk})

class OrderConfirmationView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Order
    template_name = 'orders/order_confirmation.html'
    context_object_name = 'order'

    def test_func(self):
        order = self.get_object()
        return self.request.user == order.customer or self.request.user.is_staff or self.request.user.role in ['ADMIN', 'PRESS', 'DELIVERY']

class DeliveryOrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'orders/delivery_orders.html'
    context_object_name = 'orders'
    paginate_by = 10

    def test_func(self):
        return self.request.user.role in ['ADMIN', 'DELIVERY']

    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return Order.objects.filter(delivery_person__isnull=False).order_by('-created_at')
        return Order.objects.filter(delivery_person=self.request.user).order_by('-created_at')
