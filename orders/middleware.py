from django.shortcuts import redirect
from django.urls import reverse

class DashboardRedirectMiddleware:
    """
    Middleware to redirect users to their respective dashboards after login.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if the user just logged in
        if request.user.is_authenticated and 'account/login/' in request.META.get('HTTP_REFERER', ''):
            # Define dashboard URLs based on user role
            dashboard_urls = {
                'CUSTOMER': 'orders:customer_dashboard',
                'PRESS': 'orders:press_dashboard',
                'DELIVERY': 'orders:delivery_dashboard',
                'ADMIN': 'orders:admin_dashboard',
            }
            
            # Get the appropriate dashboard URL based on user role
            dashboard_url = dashboard_urls.get(request.user.role, 'home')
            
            # Redirect to the dashboard
            return redirect(dashboard_url)
            
        return response
