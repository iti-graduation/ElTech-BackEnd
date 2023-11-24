"""
Serializers for product APIs
"""
from rest_framework import serializers

from django.core.mail import send_mail
from django.conf import settings

from core.models import (
    Product,
    ProductImage,
    Order,
    OrderProduct,
    Cart,
    CartProduct,
    User
)
from cart.serializers import CartProductSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    class Meta:
        model = User
        fields = ['id', 'email']
        read_only_fields = ['id', 'email']

class ProductThumbnailSerializer(serializers.ModelSerializer):
    """Serializer for product thumbnail."""

    class Meta:
        model = ProductImage
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
        model = Product
        fields = ['id', 'name', 'price', 'thumbnail']
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


class OrderProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderProduct model.
    Includes detailed product information.
    """
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderProduct
        fields = ['id', 'quantity', 'product', 'total_price']
        read_only_fields = ["id"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_price'] = instance.total_price
        representation['product'] = ProductSerializer(instance.product, context=self.context).data
        return representation


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders."""
    products = OrderProductSerializer(source='orderproduct_set', many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'user', 'products',
                  'country', 'first_name', 'last_name', 'address', 'zip', 'payment_method', 'order_note', 'created_at']
        read_only_fields = ['id', 'user', 'products']

    def to_representation(self, instance):
        """
        Add total_price to serialized data.
        """
        representation = super().to_representation(instance)
        representation['total_price'] = instance.total_price
        return representation


    def create(self, validated_data):
        """Create an order"""
        cart = Cart.objects.get(user = self.context["request"].user)
        products_data = CartProduct.objects.filter(cart=cart).all()
        order = Order.objects.create(**validated_data)
        for product_data in products_data:
            product_data = CartProductSerializer(product_data, context=self.context).data
            product = Product.objects.get(id=product_data['product']['id'])
            product.stock -= product_data['quantity']

            OrderProduct.objects.create(
                order=order, product=product, quantity=product_data['quantity'])
        # cart.delete()

        # Reset the cart
        cart.products.clear()
        cart.coupon = None
        product.save()
        cart.save()

        # Send email to user
        subject = "Order Confirmation"
        message = f'Your order has been placed successfully. The total amount is {order.total_price}.'
        from_email = settings.EMAIL_FROM
        send_mail(subject, message, from_email, [self.context["request"].user.email], fail_silently=False)

        return order
