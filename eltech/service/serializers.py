"""
Serialization of service app
"""
from rest_framework import serializers
from core.models import Service
from rest_framework.exceptions import ValidationError


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for services."""
    class Meta:
        model = Service
        fields = ['id', 'description', 'title', 'logo']
        read_only_fields = ['id']
