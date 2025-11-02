from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy

class LandingPageView(TemplateView):
    """
    Public landing page view that shows before login.
    """
    template_name = 'landing/index.html'

    def dispatch(self, request, *args, **kwargs):
        """Redirect to appropriate dashboard if user is already authenticated."""
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)


class RoleBasedDashboardView(LoginRequiredMixin, TemplateView):
    """
    View that redirects users to their role-specific dashboard.
    """
    login_url = reverse_lazy('account_login')
    
    def get_template_names(self):
        """Return the template based on user's role."""
        if self.request.user.is_superuser:
            return ['dashboard/admin_dashboard.html']
        elif hasattr(self.request.user, 'is_customer') and self.request.user.is_customer:
            return ['dashboard/customer_dashboard.html']
        elif hasattr(self.request.user, 'is_press_person') and self.request.user.is_press_person:
            return ['dashboard/press_dashboard.html']
        elif hasattr(self.request.user, 'is_delivery_partner') and self.request.user.is_delivery_partner:
            return ['dashboard/delivery_dashboard.html']
        return ['dashboard/dashboard.html']  # Fallback template
