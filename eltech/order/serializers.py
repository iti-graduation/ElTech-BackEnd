"""
Serializers for order APIs
"""
from rest_framework import serializers

from core.models import Order, OrderProduct


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price', 'user', 'products']
