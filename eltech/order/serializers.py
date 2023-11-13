"""
Serializers for product APIs
"""
from rest_framework import serializers

from core.models import (
    Product,
    Order,
    OrderProduct,
)


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'stock', 'view_count', 'category'
        ]
        read_only_fields = ['id']


class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source='product')

    class Meta:
        model = OrderProduct
        fields = ['id', 'quantity', 'product', 'product_id']
        read_only_fields = ["id"]



class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders."""
    products = OrderProductSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price', 'user', 'products']
        read_only_fields = ['id']

    def _get_or_create_products(self, products, order):
        """Handle getting or creating products as needed."""
        auth_user = self.context["request"].user
        for product in products:
            product_obj, created = OrderProduct.objects.get_or_create(
                user=auth_user,
                **product,
            )
            order.products.add(product_obj)

    # def create(self, validated_data):
    #     """Create an order"""
    #     products = validated_data.pop("products", [])
    #     order = Order.objects.create(**validated_data)
    #     self._get_or_create_ingredients(products, order)

    #     return order

    def create(self, validated_data):
        """Create an order"""
        products_data = validated_data.pop('products', [])
        order = Order.objects.create(**validated_data)
        for product_data in products_data:
            OrderProduct.objects.create(order=order, **product_data)
        return order

    def update(self, instance, validated_data):
        """Update an order."""
        products = validated_data.pop("products", None)

        if products is not None:
            instance.products.clear()
            self._get_or_create_products(products, instance)

        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)

        instance.save()
        return instance
