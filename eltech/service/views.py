from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from core.models import Service
from service import serializers


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """View for the manage service APIs"""
    serializer_class = serializers.ServiceSerializer
    queryset = Service.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list']:
            return [AllowAny()]
        elif self.action in ['retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.ServiceSerializer
        return self.serializer_class
