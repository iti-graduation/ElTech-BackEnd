"""
Serializers for cart APIs
"""
from rest_framework import serializers

from core import models


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    """
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = ['id', 'name', 'price', 'quantity']
        read_only_fields = ['id']

    def get_quantity(self, instance):
        cart_product = models.CartProduct.objects.get(product=instance, cart=self.context['cart'])
        return cart_product.quantity


class CartProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the CartProduct model.
    Includes detailed product information.
    """
    product = ProductSerializer(read_only=True)

    class Meta:
        model = models.CartProduct
        fields = ['id', 'quantity', 'product']
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Cart model.
    Includes a list of products in the cart.
    """
    products = CartProductSerializer(source='cartproduct_set', many=True, read_only=True)

    class Meta:
        model = models.Cart
        fields = ['id', 'user', 'products', 'coupon']
        read_only_fields = ['id']

    def to_representation(self, instance):
        """
        Add total_price to serialized data.
        """
        representation = super().to_representation(instance)
        representation['total_price'] = instance.total_price
        return representation


class CouponSerializer(serializers.ModelSerializer):
    """
    Serializer for the Coupon model.
    """

    class Meta:
        model = models.Coupon
        fields = ['id', 'code', 'discount', 'uses_limit']
        read_only_fields = ['id']
