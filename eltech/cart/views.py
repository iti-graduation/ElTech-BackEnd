"""
Views for the cart APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Cart, CartProduct, Coupon, Order, OrderProduct, Product

from cart import serializers


class CartViewSet(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    """
    Viewset for the Cart model.
    """
    queryset = Cart.objects.all()
    serializer_class = serializers.CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    # @extend_schema(request=serializers.CartProductSerializer)
    # @action(detail=False, methods=['post'])
    # def cart_products(self, request):
    #     """
    #     Create a product for a cart.
    #     If the product already exists in the cart, increment its quantity.
    #     If the cart does not exist, create a new one.
    #     """
    #     try:
    #         cart = Cart.objects.get(user=request.user)
    #     except Cart.DoesNotExist:
    #         # If the user doesn't have a cart, create a new one
    #         Cart.objects.create(user=request.user)
    #         cart = Cart.objects.get(user=request.user)
    #
    #     serializer = serializers.CartProductSerializer(data=request.data)
    #
    #     if serializer.is_valid():
    #         product_data = serializer.validated_data.get('product')
    #         product_id = product_data.get('id') if product_data else None
    #
    #         if product_id:
    #             cart_product, created = CartProduct.objects.get_or_create(
    #                 cart=cart, product_id=product_id, defaults={'quantity': serializer.validated_data['quantity']}
    #             )
    #         else:
    #             # Handle the case where product_id is not provided in the request
    #             return Response({"detail": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    #
    #         if not created:
    #             cart_product.quantity += serializer.validated_data['quantity']
    #             cart_product.save()
    #
    #         # Serialize the CartProduct instance with context
    #         cart_product_serializer = serializers.CartProductSerializer(cart_product, context={'cart': cart})
    #         return Response(cart_product_serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=serializers.CartProductSerializer)
    @action(detail=True, methods=['post'])
    def cart_products(self, request, pk=None):
        """Create a product for a cart."""
        cart = self.get_object()
        product = get_object_or_404(Product, id=request.data.get('product'))
        quantity = int(request.data.get('quantity'))

        if product.stock < quantity:
            return Response({"detail": "Product stock is not enough."}, status=status.HTTP_400_BAD_REQUEST)

        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product)
        if created:
            cart_product.quantity = quantity
        else:
            cart_product.quantity += quantity

        if cart_product.quantity > product.stock:
            return Response({"detail": "Product stock is not enough."}, status=status.HTTP_400_BAD_REQUEST)

        cart_product.save()

        serializer = serializers.CartProductSerializer(cart_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=serializers.CartProductSerializer)
    @action(detail=False, methods=['delete'], url_path='products/(?P<product_id>[^/.]+)')
    def delete_cart_product(self, request, product_id=None):
        """
        Delete a product for a cart.
        """
        cart = Cart.objects.get(user=request.user)

        try:
            product = CartProduct.objects.get(id=product_id, cart=cart)
        except CartProduct.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        product.delete()

        # Delete the cart if it's empty
        if not cart.products.exists():
            cart.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=serializers.CouponSerializer)
    @action(detail=False, methods=['post'], url_path='apply-coupon')
    def apply_coupon(self, request):
        """
        Apply a coupon to a cart.
        """
        cart = get_object_or_404(Cart, user=request.user)
        serializer = serializers.CouponSerializer(data=request.data)

        if serializer.is_valid():
            coupon = Coupon.objects.filter(code=serializer.validated_data['code'], uses_limit__gt=0).first()
            if coupon:
                cart.coupon = coupon
                cart.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='place-order')
    def place_order(self, request, pk=None):
        """Place an order."""
        cart = self.get_object()
        order = Order.objects.create(user=request.user, total_price=cart.total_price)

        for cart_product in cart.products.all():
            OrderProduct.objects.create(order=order, product=cart_product.product, quantity=cart_product.quantity)

        cart.delete()

        return Response({"detail": "Order placed successfully."}, status=status.HTTP_200_OK)
