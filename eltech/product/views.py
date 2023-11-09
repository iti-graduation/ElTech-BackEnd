"""
Views for the product APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework import viewsets, mixins, status

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Product

from product import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "is_featured",
                OpenApiTypes.INT,
                enum=[0, 1],
                description="Get featured products only.",
            )
        ]
    )
)
class ProductViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Views for manage product APIs."""

    serializer_class = serializers.ProductDetailSerializer
    queryset = Product.objects.all()

    def get_queryset(self):
        """Filter queryset for products."""
        is_featured = bool(int(self.request.query_params.get("is_featured", 0)))
        queryset = self.queryset

        if is_featured:
            queryset = queryset.filter(is_featured=True)
        else:
            queryset = queryset.filter(is_featured=False)

        return queryset.order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.ProductSerializer

        return self.serializer_class
