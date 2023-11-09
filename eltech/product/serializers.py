"""
Serializers for product APIs
"""
from rest_framework import serializers

from core.models import Product, WeeklyDeal


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'is_hot', 'is_on_sale', 'sale_amount']
        read_only_fields = ['id']


class ProductDetailSerializer(ProductSerializer):
    """Serializer for product detail view."""

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['description', 'stock']


class WeeklyDealSerializer(serializers.ModelSerializer):
    """Serializer for weekly deals."""
    product = ProductSerializer(read_only=True)

    class Meta:
        model = WeeklyDeal
        fields = ['id', 'deal_time', 'product']
        read_only_fields = ['id']
