from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.forms import inlineformset_factory
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction
import logging

# Set up logging
logger = logging.getLogger(__name__)
from .models import Order, OrderItem, ClothType
from .forms import OrderForm, OrderItemForm, get_order_item_formset

# Define the formset for order items
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.role == 'CUSTOMER':
            return Order.objects.filter(customer=self.request.user).order_by('-created_at')
        return Order.objects.all().order_by('-created_at')

class OrderCreateView(LoginRequiredMixin, CreateView):
    """View for creating new orders with order items."""
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:list')

    def get_form_kwargs(self):
        """Add user to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    def get_context_data(self, **kwargs):
        """Add formset to the template context."""
        context = super().get_context_data(**kwargs)
        
        # Initialize the formset with the current user and instance
        formset = get_order_item_formset(
            user=self.request.user,
            data=self.request.POST if self.request.method == 'POST' else None,
            instance=self.object,
            prefix='items',
            queryset=OrderItem.objects.none() if not self.request.method == 'POST' else None
        )
        context['formset'] = formset
            
        return context

    def validate_forms(self, form, formset):
        """Validate both the main form and formset."""
        form_is_valid = form.is_valid()
        formset_is_valid = formset.is_valid()
        
        # Log form errors if any
        if not form_is_valid:
            logger.error('Form validation failed. Errors: %s', form.errors)
            
        # Log formset errors if any
        if not formset_is_valid:
            logger.error('Formset validation failed. Errors: %s', formset.errors)
            
        # Check if we have at least one non-deleted item with data
        has_valid_items = False
        for form in formset:
            if not hasattr(form, 'cleaned_data'):
                continue
                
            # Skip deleted forms
            if form.cleaned_data.get('DELETE', False):
                continue
                
            # Check if the form has any data
            if any(field for field in form.cleaned_data if field != 'id' and form.cleaned_data[field]):
                has_valid_items = True
                break
                
        if not has_valid_items:
            error_msg = "At least one item is required to create an order."
            logger.error(error_msg)
            if formset_is_valid:  # Only add error if formset was otherwise valid
                formset._non_form_errors = formset.error_class([error_msg])
                formset_is_valid = False
            
        return form_is_valid and formset_is_valid, {
            'form_errors': form.errors if not form_is_valid else {},
            'formset_errors': formset.errors if not formset_is_valid else {}
        }

    def save_order_items(self, order, formset):
        """Save order items from the formset."""
        saved_items = []
        
        for form in formset:
            # Skip deleted or empty forms
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                continue
                
            item = form.save(commit=False)
            if not item.cloth_type:
                continue
                
            item.order = order
            
            # Set default values if not provided
            if not item.quantity:
                item.quantity = 1
                
            # Calculate prices
            if not item.unit_price:
                item.unit_price = item.cloth_type.price_per_unit
                
            item.total_price = item.unit_price * item.quantity
            
            # Save the item
            item.save()
            saved_items.append(item)
            
        return saved_items

    def form_valid(self, form):
        """Handle valid form submission."""
        is_ajax = self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        context = self.get_context_data()
        formset = context['formset']
        
        # Validate both forms
        is_valid, errors = self.validate_forms(form, formset)
        
        if not is_valid:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    **errors,
                    'message': 'Please correct the errors below.'
                }, status=400)
            return self.form_invalid(form)
        
        try:
            with transaction.atomic():
                # Save the order
                self.object = form.save(commit=False)
                self.object.customer = self.request.user
                self.object.save()
                
                # Process the formset
                instances = formset.save(commit=False)
                
                # Delete any instances marked for deletion
                for obj in formset.deleted_objects:
                    if obj.pk:
                        obj.delete()
                
                # Save new and updated instances
                for instance in instances:
                    if not instance.quantity or int(instance.quantity) <= 0:
                        continue
                    instance.order = self.object
                    instance.save()
                
                # Update order total
                self.object.calculate_total()
                
                messages.success(self.request, 'Order created successfully!')
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'redirect': self.get_success_url()
                    })
                return redirect(self.get_success_url())
                    
        except Exception as e:
            logger.error('Error saving order: %s', str(e), exc_info=True)
            messages.error(self.request, 'An error occurred while saving the order. Please try again.')
            # Handle form errors
            for field, error_list in errors.get('form_errors', {}).items():
                for error in error_list:
                    messages.error(self.request, f"{field}: {error}")
                    
            for form_errors in errors.get('formset_errors', {}).values():
                for error in form_errors:
                    if isinstance(error, str):
                        messages.error(self.request, f"Item: {error}")
                    elif isinstance(error, list):
                        for sub_error in error:
                            messages.error(self.request, f"Item: {sub_error}")
                        
            return self.form_invalid(form)
        
    def form_invalid(self, form):
        """Handle invalid form submission."""
        context = self.get_context_data()
        context['form'] = form
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'form_errors': form.errors,
                'formset_errors': context['formset'].errors if 'formset' in context else {},
                'message': 'Please correct the errors below.'
            }, status=400)
            
        return self.render_to_response(context)
        
    def get_success_url(self):
        return reverse('orders:detail', kwargs={'pk': self.object.pk})

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    context_object_name = 'order'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items'] = get_order_item_formset(
                user=self.request.user,
                data=self.request.POST,
                instance=self.object,
                prefix='items'
            )
        else:
            context['items'] = get_order_item_formset(
                user=self.request.user,
                instance=self.object,
                prefix='items'
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        
        if items.is_valid() and form.is_valid():
            self.object = form.save()
            
            # Save order items
            items.instance = self.object
            items.save()
            
            # Update order total
            self.object.update_total()
            
            messages.success(self.request, 'Order updated successfully!')
            return redirect('orders:detail', pk=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def test_func(self):
        order = self.get_object()
        return self.request.user.is_staff or order.customer == self.request.user

    def get_success_url(self):
        return reverse('orders:detail', kwargs={'pk': self.object.pk})

class OrderDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:list')
    context_object_name = 'order'

    def test_func(self):
        order = self.get_object()
        return self.request.user == order.customer or self.request.user.is_admin

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Order deleted successfully.')
        return super().delete(request, *args, **kwargs)


class PressOrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'orders/press_order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_press or self.request.user.is_admin

    def get_queryset(self):
        return Order.objects.filter(
            status__in=['PENDING', 'IN_PROGRESS'],
            press_person=self.request.user
        ).order_by('pickup_date')


class DeliveryOrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'orders/delivery_order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_delivery or self.request.user.is_admin

    def get_queryset(self):
        return Order.objects.filter(
            status__in=['READY_FOR_DELIVERY', 'OUT_FOR_DELIVERY'],
            delivery_person=self.request.user
        ).order_by('delivery_date')
