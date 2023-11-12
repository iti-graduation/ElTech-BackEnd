# service/views.py

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

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
        serializer.save(user=self.request.user)
