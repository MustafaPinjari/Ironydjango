from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from .models import Service, ServiceOption, ServiceVariant
from .serializers import ServiceOptionSerializer
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

class ServiceOptionViewSet(viewsets.ViewSet):
    """
    API endpoint that allows service options to be viewed.
    """
    def list(self, request):
        """
        List all active options for a specific service.
        """
        service_id = request.query_params.get('service_id')
        variant_id = request.query_params.get('variant_id')
        
        if not service_id:
            return Response(
                {"error": "service_id parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get options for the service
            options = ServiceOption.objects.filter(
                service_id=service_id,
                is_active=True
            ).order_by('display_order')
            
            # If variant_id is provided, filter options that apply to this variant
            if variant_id:
                try:
                    variant = ServiceVariant.objects.get(id=variant_id, is_active=True)
                    # Here you can add logic to filter options based on variant if needed
                    # For now, we'll return all options for the service
                except ServiceVariant.DoesNotExist:
                    pass
            
            # Serialize the options with their choices
            serializer = ServiceOptionSerializer(options, many=True, context={'request': request})
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching options: {str(e)}")
            return Response(
                {"error": "An error occurred while fetching options"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
