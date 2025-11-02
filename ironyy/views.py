"""
Views for the main ironyy project.
"""
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import messages


class LandingPageView(TemplateView):
    """Landing page view for unauthenticated users."""
    template_name = 'ironyy/landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_year'] = timezone.now().year
        return context


def handler400(request, exception=None):
    """Custom 400 error handler."""
    context = {
        'title': _('400 Bad Request'),
        'error_message': _('The request could not be understood by the server.'),
    }
    return render(request, 'errors/400.html', context, status=400)


def handler403(request, exception=None):
    """Custom 403 error handler."""
    context = {
        'title': _('403 Forbidden'),
        'error_message': _('You do not have permission to access this page.'),
    }
    return render(request, 'errors/403.html', context, status=403)


def handler404(request, exception=None):
    """Custom 404 error handler."""
    context = {
        'title': _('404 Page Not Found'),
        'error_message': _('The page you are looking for does not exist.'),
    }
    return render(request, 'errors/404.html', context, status=404)


def handler500(request):
    """Custom 500 error handler."""
    context = {
        'title': _('500 Server Error'),
        'error_message': _('An error occurred on the server. Please try again later.'),
    }
    return render(request, 'errors/500.html', context, status=500)


class HomeView(View):
    """Home page view."""
    template_name = 'dashboard/home.html'
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET request.
        
        Args:
            request: The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            HttpResponse: Rendered template with context.
        """
        context = {
            'title': _('Welcome to Ironyy'),
        }
        return render(request, self.template_name, context)
