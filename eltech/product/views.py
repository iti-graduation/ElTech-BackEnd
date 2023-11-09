"""
Views for the product APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework import views, viewsets, mixins, status

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Product, WeeklyDeal

from product import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "is_featured",
                OpenApiTypes.INT,
                enum=[0, 1],
                description="Get featured products only.",
            ),
            OpenApiParameter(
                "is_trending",
                OpenApiTypes.INT,
                enum=[0, 1],
                description="Get trending products only.",
            ),
            OpenApiParameter(
                "is_popular",
                OpenApiTypes.INT,
                enum=[0, 1],
                description="Get popular products only.",
            ),
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
        is_trending = bool(int(self.request.query_params.get("is_trending", 0)))
        is_popular = bool(int(self.request.query_params.get("is_popular", 0)))
        queryset = self.queryset

        if is_featured:
            queryset = queryset.filter(is_featured=True)

        if is_trending:
            queryset = queryset.filter(is_trending=True)

        if is_popular:
            queryset = queryset.order_by('-view_count')

        return queryset

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.ProductSerializer

        return self.serializer_class


class WeeklyDealView(views.APIView):
    """View for the weekly deal."""

    def get(self, request):
        weekly_deal = WeeklyDeal.objects.latest('deal_time')
        serializer = serializers.WeeklyDealSerializer(weekly_deal)
        return Response(serializer.data)
