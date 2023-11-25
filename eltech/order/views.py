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
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework import generics

from django.core.mail import send_mail
from django.conf import settings

from core.models import Order
from order import serializers


class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
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

    @action(detail=False, methods=['patch'], url_path='update/(?P<order_id>[^/.]+)')
    def update_order(self, request, order_id=None):
        """update an order."""
        order = Order.objects.get(id=order_id)
        order_status = request.data.get('status')
        order.status = order_status

        order.save()
        serializer = serializers.OrderSerializer(order, context={'request': request})

        # Send email to user
        subject = "Order Status Update"
        message = f'Your order status has been updated to {order_status}.'
        from_email = settings.EMAIL_FROM
        send_mail(subject, message, from_email, [order.user.email], fail_silently=False)

        return Response(serializer.data, status=status.HTTP_200_OK)



class OrderListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.all().order_by('id')


class OrderRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.all().order_by('id')
