from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.forms import inlineformset_factory
from django.utils import timezone
from .models import Order, OrderItem, ClothType
from .forms import OrderForm, OrderItemForm

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_customer:
            return Order.objects.filter(customer=self.request.user).order_by('-created_at')
        return Order.objects.all().order_by('-created_at')

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items'] = OrderItemFormSet(self.request.POST, prefix='items')
        else:
            context['items'] = OrderItemFormSet(prefix='items')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        
        if items.is_valid() and form.is_valid():
            order = form.save(commit=False)
            order.customer = self.request.user
            order.save()
            
            # Save order items
            for item in items:
                if item.cleaned_data.get('cloth_type'):
                    order_item = item.save(commit=False)
                    order_item.order = order
                    order_item.unit_price = order_item.cloth_type.price_per_unit
                    order_item.save()
            
            # Update order total
            order.update_total()
            
            messages.success(self.request, 'Order created successfully!')
            return redirect('orders:detail', pk=order.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))

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
            context['items'] = OrderItemFormSet(
                self.request.POST, 
                instance=self.object,
                prefix='items'
            )
        else:
            context['items'] = OrderItemFormSet(
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
        return self.request.user.is_staff or order.customer == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Order deleted successfully!')
        return super().delete(request, *args, **kwargs)
