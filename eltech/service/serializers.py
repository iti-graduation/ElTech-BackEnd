"""
Serialization of service app
"""
from rest_framework import serializers
from core.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for services."""
    class Meta:
        model = Service
        fields = ['id', 'title', 'logo']
        read_only_fields = ['id']


class ServiceDetailSerializer(ServiceSerializer):
    """Serializer for service detail view."""

    class Meta(ServiceSerializer.Meta):
        fields = ServiceSerializer.Meta.fields + ['description']
