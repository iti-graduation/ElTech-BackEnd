The id is still asked for when retrieving or deleting cart.
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

from core.models import Cart, CartProduct, Coupon, Order, OrderProduct

from cart import serializers


class CartViewSet(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    Viewset for the Cart model.
    """
    queryset = Cart.objects.all()
    serializer_class = serializers.CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the cart for the request user.
        """
        cart = get_object_or_404(Cart, user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete the cart for the request user.
        """
        cart = get_object_or_404(Cart, user=request.user)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=serializers.CartProductSerializer)
    @action(detail=False, methods=['post'])
    def cart_products(self, request):
        """
        Create a product for a cart.
        If the product already exists in the cart, increment its quantity.
        If the cart does not exist, create a new one.
        """
        cart, _ = Cart.objects.get_or_create(user=request.user)  # Get or create a cart for the user
        serializer = serializers.CartProductSerializer(data=request.data)

        if serializer.is_valid():
            product_id = serializer.validated_data['product'].id
            cart_product, created = CartProduct.objects.get_or_create(
                cart=cart, product_id=product_id, defaults={'quantity': serializer.validated_data['quantity']}
            )

            if not created:
                cart_product.quantity += serializer.validated_data['quantity']
                cart_product.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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