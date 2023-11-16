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
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination

from django.db.models import Q

from core.models import Product, WeeklyDeal, Category, Review

from product import serializers


class ProductPagination(PageNumberPagination):
    page_size = 12


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
            OpenApiParameter(
                "q",
                OpenApiTypes.STR,
                description="Search products by name or description.",
            ),
            OpenApiParameter(
                "category",
                OpenApiTypes.INT,
                description="Get products according to category id.",
            ),
        ]
    )
)
class ProductViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Views for manage product APIs."""

    serializer_class = serializers.ProductDetailSerializer
    queryset = Product.objects.all()
    authentication_classes = [TokenAuthentication]
    filter_backends = [OrderingFilter]
    ordering_fields = ["price"]
    pagination_class = ProductPagination

    def get_queryset(self):
        """Filter queryset for products."""
        is_featured = bool(int(self.request.query_params.get("is_featured", 0)))
        is_trending = bool(int(self.request.query_params.get("is_trending", 0)))
        is_popular = bool(int(self.request.query_params.get("is_popular", 0)))
        category = self.request.query_params.get('category', None)
        # ordering = self.request.query_params.get("ordering", 0)
        query = self.request.query_params.get("q")
        queryset = self.queryset.prefetch_related('ratings')

        if category is not None:
            queryset = queryset.filter(category__id=category)

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        if is_featured:
            queryset = queryset.filter(is_featured=True)

        if is_trending:
            queryset = queryset.filter(is_trending=True)

        if is_popular:
            queryset = queryset.order_by("-view_count")

        return queryset

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ["ratings", "reviews"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return serializers.ProductSerializer

        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a product and increment the views_count."""
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(request=serializers.ReviewSerializer)
    @action(detail=True, methods=["post"])
    def reviews(self, request, pk=None):
        """Create a review for a product."""
        product = self.get_object()
        serializer = serializers.ReviewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=serializers.RatingSerializer)
    @action(detail=True, methods=["post"])
    def ratings(self, request, pk=None):
        """Create a rating for a product."""
        product = self.get_object()
        serializer = serializers.RatingSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=serializers.ReviewSerializer)
    @action(detail=True, methods=["delete"], url_path="reviews/(?P<review_id>[^/.]+)")
    def delete_review(self, request, pk=None, review_id=None):
        """Delete a review for a product."""
        product = self.get_object()

        try:
            review = Review.objects.get(id=review_id, product=product)
        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Check if the user is the owner of the review
        if review.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Views for manage category APIs."""

    serializer_class = serializers.CategoryDetailSerializer
    queryset = Category.objects.all()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return serializers.CategorySerializer

        return self.serializer_class


class WeeklyDealViewSet(viewsets.GenericViewSet):
    """Views for manage weekly deal APIs."""

    serializer_class = serializers.WeeklyDealSerializer
    queryset = WeeklyDeal.objects.all()

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """Retrieve the latest weekly deal."""
        weekly_deal = WeeklyDeal.objects.latest("deal_time")
        serializer = self.get_serializer(weekly_deal)
        return Response(serializer.data)
