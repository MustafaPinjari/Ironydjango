from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from services.models import Service, ServiceVariant, ServiceOption
from services.serializers import ServiceVariantSerializer

class ServiceViewSet(viewsets.ViewSet):
    """
    API endpoint that allows services to be viewed.
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access by default

    @action(detail=False, methods=['get'])
    def variants(self, request):
        """
        Get variants for a specific service
        """
        import logging
        logger = logging.getLogger(__name__)
        
        service_id = request.query_params.get('service_id')
        logger.info(f"Received request for variants with service_id: {service_id}")
        
        if not service_id:
            logger.warning("No service_id provided in request")
            return Response(
                {"error": "service_id parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service_id = int(service_id)
            logger.info(f"Looking for variants with service_id={service_id}")
            
            # Get all active variants for the service
            variants = ServiceVariant.objects.filter(
                service_id=service_id,
                is_active=True
            ).select_related('service')
            
            logger.info(f"Found {variants.count()} variants for service_id={service_id}")
            
            # For debugging: log all service IDs and names
            all_services = Service.objects.values_list('id', 'name')
            logger.info(f"All services in DB: {list(all_services)}")
            
            # Calculate final price (base price + adjustment)
            variants_data = []
            for variant in variants:
                variant_data = ServiceVariantSerializer(variant).data
                variant_data['final_price'] = float(variant.service.base_price + variant.price_adjustment)
                variants_data.append(variant_data)
                logger.debug(f"Variant {variant.id}: {variant.name}, Price: {variant_data['final_price']}")
                
            return Response(variants_data)
            
        except ValueError:
            logger.error(f"Invalid service_id format: {service_id}")
            return Response(
                {"error": "service_id must be an integer"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Error in variants endpoint")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def options(self, request):
        """
        Get options for a specific service
        """
        service_id = request.query_params.get('service_id')
        if not service_id:
            return Response(
                {"error": "service_id parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        options = ServiceOption.objects.filter(
            service_id=service_id,
            is_active=True
        )
        
        return Response([{
            'id': opt.id,
            'name': opt.name,
            'description': opt.description,
            'price_adjustment': float(opt.price_adjustment)
        } for opt in options])
