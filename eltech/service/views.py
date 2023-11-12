from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from core.models import Service
from service import serializers  


class ServiceViewSet(viewsets.ModelViewSet):
    """View for the manage service APIs"""
    serializer_class = serializers.ServiceDetailSerializer
    queryset = Service.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.ServiceSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new service"""
        title = serializer.validated_data['title']
        existing_service = Service.objects.filter(title=title)

        if existing_service.exists():
            raise serializers.ValidationError(
                "Service with this title already exists.")

        serializer.save()
