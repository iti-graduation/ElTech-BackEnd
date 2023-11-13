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

from core.models import Order, OrderProduct, Product

from order.serializers import OrderSerializer, OrderProductSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @extend_schema(request=OrderProductSerializer)
    @action(detail=True, methods=['post'])
    def order_products(self, request, pk=None):
        """Create a product for a order."""
        order = self.get_object()
        product = get_object_or_404(Product, id=request.data.get('product'))
        quantity = int(request.data.get('quantity'))

        if product.stock < quantity:
            return Response({"detail": "Product stock is not enough."}, status=status.HTTP_400_BAD_REQUEST)

        order_product, created = OrderProduct.objects.get_or_create(order=order, product=product)
        if created:
            order_product.quantity = quantity
        else:
            order_product.quantity += quantity

        if order_product.quantity > product.stock:
            return Response({"detail": "Product stock is not enough."}, status=status.HTTP_400_BAD_REQUEST)

        order_product.save()

        serializer = OrderProductSerializer(order_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
