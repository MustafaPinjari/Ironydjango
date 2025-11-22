from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from .models import Order, OrderItem
from accounts.models import User

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
from django.utils import timezone

logger = logging.getLogger(__name__)

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_type', 'pickup_address', 'delivery_address', 
                 'preferred_pickup_date', 'preferred_delivery_date', 'special_instructions']
        widgets = {
            'preferred_pickup_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'preferred_delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'special_instructions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make delivery date not required
        self.fields['preferred_delivery_date'].required = False
        
        # Set minimum date to today
        today = timezone.now().date()
        self.fields['preferred_pickup_date'].widget.attrs['min'] = today
        self.fields['preferred_delivery_date'].widget.attrs['min'] = today

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'

    def get_form(self, form_class=None):
        logger.debug("Entering get_form")
        form = super().get_form(form_class)
        logger.debug(f"Form fields: {form.fields.keys()}")
        return form

    def form_valid(self, form):
        logger.debug("Entering form_valid")
        try:
            form.instance.customer = self.request.user
            form.instance.status = Order.Status.PENDING
            
            # Set default delivery date to pickup date if not provided
            if not form.cleaned_data.get('preferred_delivery_date') and form.cleaned_data.get('delivery_type') == 'delivery':
                form.instance.preferred_delivery_date = form.cleaned_data.get('preferred_pickup_date')
            
            logger.debug(f"Form data before save: {form.cleaned_data}")
            
            # Save the form and get the order instance
            self.object = form.save()
            logger.info(f"Order created successfully: {self.object.order_number}")
            
            # Add success message
            messages.success(self.request, 'Order created successfully! What would you like to do next?')
            
            # Log the redirect URL
            redirect_url = self.get_success_url()
            logger.debug(f"Redirecting to: {redirect_url}")
            
            # Use HttpResponseRedirect to ensure proper redirection
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(redirect_url)
            
        except Exception as e:
            logger.error(f"Error in form_valid: {str(e)}", exc_info=True)
            messages.error(self.request, 'There was an error processing your order. Please try again.')
            return self.form_invalid(form)
    
    def get_success_url(self):
        try:
            if not hasattr(self, 'object') or not self.object or not self.object.pk:
                logger.error("No valid order object found for redirection")
                return reverse_lazy('orders:list')
                
            url = reverse_lazy('orders:order_confirmation', kwargs={'pk': self.object.pk})
            logger.debug(f"Success URL: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Error generating success URL: {str(e)}")
            return reverse_lazy('orders:list')
            
    def form_invalid(self, form):
        logger.warning(f"Form is invalid. Errors: {form.errors}")
        return super().form_invalid(form)

class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Order
    template_name = 'orders/order_form.html'
    fields = ['status', 'shipping_address', 'payment_status']

    def test_func(self):
        order = self.get_object()
        return self.request.user.is_staff or order.customer == self.request.user

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
        return self.request.user.is_staff or order.customer == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Order deleted successfully!')
        return super().delete(request, *args, **kwargs)

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

class OrderConfirmationView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Order
    template_name = 'orders/order_confirmation.html'
    context_object_name = 'order'
    
    def test_func(self):
        order = self.get_object()
        return self.request.user == order.customer or self.request.user.role in ['ADMIN', 'PRESS', 'DELIVERY']

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
