"""
Serializers for cart APIs
"""
from rest_framework import serializers

from core import models


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    """
    class Meta:
        model = models.Product
        fields = ['id', 'name', 'price']
        read_only_fields = ['id']


class CartProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the CartProduct model.
    Includes detailed product information.
    """
    product = serializers.PrimaryKeyRelatedField(queryset=models.Product.objects.all())

    class Meta:
        model = models.CartProduct
        fields = ['id', 'quantity', 'product']
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = ProductSerializer(instance.product, context=self.context).data
        return representation


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Cart model.
    Includes a list of products in the cart.
    """
    products = CartProductSerializer(source='cartproduct_set', many=True, read_only=True)

    class Meta:
        model = models.Cart
        fields = ['id', 'user', 'products']
        read_only_fields = ['id', 'user']

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


class ApplyCouponSerializer(serializers.ModelSerializer):
    """
    Serializer for applying a coupon to a cart.
    """

    class Meta:
        model = models.Cart
        fields = ['id', 'user', 'products', 'coupon']
        read_only_fields = ['id']
