"""
Views for the order APIs.
"""

from rest_framework import (
    viewsets,
    mixins,
    status
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Order
from order import serializers


class OrderViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    """View for manage order APIs."""

    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve orders for authenticated user."""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new order."""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['patch'], url_path='update')
    def update_order(self, request, pk=None):
        """update an order."""
        order = Order.objects.get(user=request.user)
        order_status = request.data.get('status')
        order.status = order_status

        order.save()
        serializer = serializers.OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

