from django.shortcuts import render
from django.views.generic import View
from django.utils.translation import gettext_lazy as _


class HomeView(View):
    """
    View for the dashboard home page.
    """
    template_name = 'dashboard/home.html'
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET request.
        """
        context = {
            'page_title': _('Dashboard'),
        }
        return render(request, self.template_name, context)
