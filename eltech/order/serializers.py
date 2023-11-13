"""
Serializers for order APIs
"""
from rest_framework import serializers

from core.models import Product, Order, OrderProduct


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    """
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']
        read_only_fields = ['id']


class OrderProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderProduct model.
    Includes detailed product information.
    """
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderProduct
        fields = ['id', 'quantity', 'product']
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = ProductSerializer(instance.product, context=self.context).data
        return representation


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
    Includes a list of products in the cart.
    """
    products = OrderProductSerializer(source='orderproduct_set', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'products']
        read_only_fields = ['id', 'user']

    def to_representation(self, instance):
        """
        Add total_price to serialized data.
        """
        representation = super().to_representation(instance)
        representation['total_price'] = instance.total_price
        return representation
