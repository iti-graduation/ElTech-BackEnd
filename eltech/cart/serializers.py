"""
Serializers for cart APIs
"""
from rest_framework import serializers

from core import models


class ProductThumbnailSerializer(serializers.ModelSerializer):
    """Serializer for product thumbnail."""

    class Meta:
        model = models.ProductImage
        fields = ['image']
        read_only_fields = ['image']

    def to_representation(self, instance):
        """Only return the image if it is a thumbnail."""
        if instance.is_thumbnail:
            return {'image': self.context['request'].build_absolute_uri(instance.image.url)}
        return {}


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""
    thumbnail = ProductThumbnailSerializer(read_only=True)

    class Meta:
        model = models.Product
        fields = ['id', 'name', 'price', 'stock', 'thumbnail']
        read_only_fields = ['id']

    def to_representation(self, instance):
        """Add thumbnail to serialized data."""
        representation = super().to_representation(instance)

        thumbnail = instance.images.filter(is_thumbnail=True).first()
        if thumbnail:
            representation['thumbnail'] = ProductThumbnailSerializer(thumbnail, context=self.context).data
        else:
            representation['thumbnail'] = {}

        return representation


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
        representation['total_price'] = instance.total_price
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
        read_only_fields = ['id', 'discount', 'uses_limit']


class ApplyCouponSerializer(serializers.ModelSerializer):
    """
    Serializer for applying a coupon to a cart.
    """

    class Meta:
        model = models.Cart
        fields = ['id', 'user', 'products', 'coupon']
        read_only_fields = ['id']

