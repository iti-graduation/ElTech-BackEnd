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
from django.core.mail import send_mail
from django.conf import settings

from core.models import (
    Product,
    WeeklyDeal,
    Category,
    Review,
    ProductFeature,
    ProductImage,
    ProductNotification,
)

from product import serializers

import logging

logger = logging.getLogger(__name__)


class ProductPagination(PageNumberPagination):
    page_size = 12

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "page_number": self.page.number,  # Add this line
                "results": data,
            }
        )


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
class ProductViewSet(viewsets.ModelViewSet):
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
        category = self.request.query_params.get("category", None)
        # ordering = self.request.query_params.get("ordering", 0)
        query = self.request.query_params.get("q")
        queryset = self.queryset.prefetch_related("ratings")

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
            queryset = queryset.order_by("-view_count")[:12]

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

        # if self.action == "create":
        # return serializers.ProductCreateSerializer

        if self.action in ["create", "partial_update"]:
            return serializers.ProductCreateSerializer

        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a product and increment the views_count."""
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        old_stock = product.stock
        response = super().update(request, *args, **kwargs)
        product.refresh_from_db()
        new_stock = product.stock
        if old_stock == 0 and new_stock > 0:
            notifications = ProductNotification.objects.filter(product=product)
            for notification in notifications:
                for user in notification.users.all():
                    send_mail(
                        'Product Available',
                        f'The product {product.name} is now available.',
                        settings.EMAIL_FROM,
                        [user.email],
                        fail_silently=False,
                    )
                notification.delete()
        return response

    # @action(detail=True, methods=["post"])
    # def notify(self, request, pk=None):
    #     """Add a product to the user's notifications."""
    #     product = self.get_object()
    #     notification, created = ProductNotification.objects.get_or_create(product=product)
    #     notification.users.add(request.user)
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    
    # from drf_spectacular.utils import extend_schema

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def notify(self, request, pk=None):
        """Add a product to the user's notifications."""
        product = self.get_object()
        notification, created = ProductNotification.objects.get_or_create(product=product)
        notification.users.add(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

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

    @action(detail=True, methods=["post"])
    def upload_image(self, request, pk=None):
        product = self.get_object()
        serializer = serializers.ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def add_feature(self, request, pk=None):
        product = self.get_object()
        serializer = serializers.ProductFeatureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    """Views for manage category APIs."""

    serializer_class = serializers.CategoryDetailSerializer
    queryset = Category.objects.all()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return serializers.CategorySerializer

        return self.serializer_class


class WeeklyDealViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """Views for manage weekly deal APIs."""

    serializer_class = serializers.WeeklyDealSerializer
    queryset = WeeklyDeal.objects.all()

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """Retrieve the latest weekly deal."""
        try:
            weekly_deal = WeeklyDeal.objects.latest("deal_time")
        except WeeklyDeal.DoesNotExist:
            return Response(
                {"detail": "No weekly deal available"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(weekly_deal)
        return Response(serializer.data)


# class ProductImageUploadView(views.APIView):
#     def post(self, request, *args, **kwargs):
#         print(request.data)
#         product_id = kwargs.get('product_id')
#         product = Product.objects.get(id=product_id)
#         serializer = serializers.ProductImageSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(product=product)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class ProductFeatureAddView(views.APIView):
#     def post(self, request, *args, **kwargs):
#         print(request.data)
#         product_id = kwargs.get('product_id')
#         product = Product.objects.get(id=product_id)
#         serializer = serializers.ProductFeatureSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(product=product)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductFeatureViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """Views for manage product features APIs."""

    serializer_class = serializers.ProductFeatureCreateSerializer
    queryset = ProductFeature.objects.all()

    def create(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        feature = request.data.get("feature")

        if not product_id or not feature:
            return Response(
                {"detail": "product_id and feature are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        # Delete all existing images related to the product
        product.features.all().delete()

        product_feature = ProductFeature.objects.create(
            product=product, feature=feature
        )

        serializer = self.get_serializer(product_feature)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


from rest_framework import viewsets, status
from rest_framework.response import Response


class ProductImageViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """ViewSet for product images API."""

    serializer_class = serializers.ProductImageCreateSerializer
    queryset = ProductImage.objects.all()

    # def create(self, request, *args, **kwargs):
    #     print(request.data)
    #     serializer = self.get_serializer(data=request.data)
    #     if serializer.is_valid():
    #         product_id = serializer.validated_data.pop('product_id')
    #         product = Product.objects.get(id=product_id)
    #         image = ProductImage.objects.create(product=product, **serializer.validated_data)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def create(self, request, *args, **kwargs):
    #     print(request.data)
    #     serializer = self.get_serializer(data=request.data)
    #     if serializer.is_valid():
    #         product = serializer.validated_data.get('product')
    #         image = ProductImage.objects.create(product=product, **serializer.validated_data)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def create(self, request, *args, **kwargs):
    #     print(request.data)
    #     logger.info(request.data)
    #     product_id = request.data.get('product_id')
    #     image = request.data.get('image')

    #     if not product_id or not image:
    #         return Response({"detail": "product_id and image are required"}, status=status.HTTP_400_BAD_REQUEST)

    #     try:
    #         product = Product.objects.get(id=product_id)
    #     except Product.DoesNotExist:
    #         return Response({"detail": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)

    #     product_image = ProductImage.objects.create(product=product, image=image)

    #     serializer = self.get_serializer(product_image)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        print(request.data)
        product_id = request.data.get("product_id")
        image = request.data.get("image")
        is_thumbnail = request.data.get("is_thumbnail")

        # Convert is_thumbnail to boolean if it's a string
        if isinstance(is_thumbnail, str):
            if is_thumbnail.lower() == "true":
                is_thumbnail = True
            elif is_thumbnail.lower() == "false":
                is_thumbnail = False

        if not product_id or not image:
            return Response(
                {"detail": "product_id and image are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if an image with the same product_id and image already exists
        # if ProductImage.objects.filter(product=product, image=image).exists():
        #     return Response(
        #         {"detail": "Image with the same product_id and image already exists"},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        if is_thumbnail:
            product.images.all().delete()

        product_image = ProductImage.objects.create(
            product=product, image=image, is_thumbnail=is_thumbnail
        )

        # Check if an image with the same product_id and image already exists
        # print(product)

        # test_image = ProductImage.objects.get(product=product)[0]
        # print("Old Image", test_image)
        # print("New Image", image)
        # try:
        #     product_image = ProductImage.objects.get(product=product, image=image)
        #     # If the image exists, update the is_thumbnail field
        #     product_image.is_thumbnail = is_thumbnail
        #     product_image.save()
        # except ProductImage.DoesNotExist:
        #     # If the image does not exist, create a new one
        #     product_image = ProductImage.objects.create(
        #         product=product, image=image, is_thumbnail=is_thumbnail
        #     )

        serializer = self.get_serializer(product_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProductNotificationSerializer
    queryset = ProductNotification.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(users=[self.request.user])
