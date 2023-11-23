"""
Serializers for product APIs
"""
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from django.db.models import Avg

from core import models

import logging

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    class Meta:
        model = models.User
        fields = ["id", "email", "first_name", "last_name", "profile_picture"]
        read_only_fields = ["id", "email", "first_name", "last_name", "profile_picture"]


class RatingSerializer(serializers.ModelSerializer):
    """Serializer for ratings."""

    class Meta:
        model = models.Rating
        fields = ["id", "rating", "user"]
        read_only_fields = ["id", "user"]


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = models.Review
        fields = ["id", "content", "created_at", "updated_at", "user"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductFeatureSerializer(serializers.ModelSerializer):
    """Serializer for product features."""

    class Meta:
        model = models.ProductFeature
        fields = ["id", "feature"]
        read_only_fields = ["id"]


class ProductFeatureCreateSerializer(serializers.ModelSerializer):
    """Serializer for product features."""

    product_id = serializers.PrimaryKeyRelatedField(
        source="product.id", queryset=models.Product.objects.all(), write_only=True
    )

    class Meta:
        model = models.ProductFeature
        fields = ["id", "feature", "product_id"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        product_id = validated_data.pop("product_id")
        product = models.Product.objects.get(id=product_id)
        feature = models.ProductFeature.objects.create(
            product=product, **validated_data
        )
        return feature


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""

    class Meta:
        model = models.ProductImage
        fields = ["id", "image", "is_thumbnail"]
        read_only_fields = ["id"]


# class ProductImageCreateSerializer(serializers.ModelSerializer):
#     """Serializer for product images."""

#     product_id = serializers.PrimaryKeyRelatedField(
#         source='product.id',
#         queryset=models.Product.objects.all(),
#         write_only=True
#     )

#     class Meta:
#         model = models.ProductImage
#         fields = ['id', 'image', 'is_thumbnail', 'product_id']
#         read_only_fields = ['id']

#     def create(self, validated_data):
#         print(validated_data)
#         product_id = validated_data.pop('product_id')
#         product = models.Product.objects.get(id=product_id)
#         image = models.ProductImage.objects.create(product=product, **validated_data)
#         return image


class ProductImageCreateSerializer(serializers.ModelSerializer):
    """Serializer for product images."""

    product_id = serializers.PrimaryKeyRelatedField(
        source="product.id", queryset=models.Product.objects.all(), write_only=True
    )

    class Meta:
        model = models.ProductImage
        fields = ["id", "image", "is_thumbnail", "product_id"]
        read_only_fields = ["id"]

    def to_internal_value(self, data):
        # Convert is_thumbnail to boolean
        print(data)
        logger.info(data)
        is_thumbnail = data.get("is_thumbnail")
        if isinstance(is_thumbnail, str):
            if is_thumbnail.lower() == "true":
                data["is_thumbnail"] = True
            elif is_thumbnail.lower() == "false":
                data["is_thumbnail"] = False
        return super().to_internal_value(data)

    def create(self, validated_data):
        print(validated_data)
        product_id = validated_data.pop("product_id")
        product = models.Product.objects.get(id=product_id)

        # Delete all existing images related to the product
        # product.images.all().delete()

        image = models.ProductImage.objects.create(product=product, **validated_data)
        return image

    def update(self, instance, validated_data):
        product_id = validated_data.pop("product_id", None)
        if product_id:
            instance.product_id = product_id
        instance.image = validated_data.get("image", instance.image)
        instance.is_thumbnail = validated_data.get(
            "is_thumbnail", instance.is_thumbnail
        )
        instance.save()
        return instance


class ProductThumbnailSerializer(serializers.ModelSerializer):
    """Serializer for product thumbnail."""

    class Meta:
        model = models.ProductImage
        fields = ["image"]
        read_only_fields = ["image"]

    def to_representation(self, instance):
        """Only return the image if it is a thumbnail."""
        request = self.context.get("request")
        if request and instance.is_thumbnail:
            return {"image": request.build_absolute_uri(instance.image.url)}
        return {}


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""

    thumbnail = ProductThumbnailSerializer(read_only=True)

    class Meta:
        model = models.Product
        fields = [
            "id",
            "name",
            "price",
            "is_hot",
            "is_on_sale",
            "sale_amount",
            "thumbnail",
            "description",
            "stock",
            "is_deleted",
        ]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        """Add thumbnail to serialized data."""
        representation = super().to_representation(instance)

        thumbnail = instance.images.filter(is_thumbnail=True).first()
        if thumbnail:
            representation["thumbnail"] = ProductThumbnailSerializer(
                thumbnail, context=self.context
            ).data
        else:
            representation["thumbnail"] = {}

        return representation


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = [
            "id",
            "name",
            "price",
            "is_hot",
            "is_on_sale",
            "sale_amount",
            "description",
            "stock",
            "is_featured",
            "is_trending",
            "is_deleted",
            "category",
        ]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""

    class Meta:
        model = models.Category
        fields = ["id", "name", "image"]
        read_only_fields = ["id"]


class CustomPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return {
            "links": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            },
            "count": self.page.paginator.count,
            "page_number": self.page.number,
            "results": data,
        }


class CategoryDetailSerializer(CategorySerializer):
    """Serializer for category detail view."""

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")
        paginator = CustomPagination()
        paginator.page_size = 5  # Set the number of items per page here

        # Apply the pagination
        products = paginator.paginate_queryset(instance.products.all(), request)
        serializer = ProductSerializer(
            products, many=True, context={"request": request}
        )

        # Add the paginated results to the representation
        representation["products"] = paginator.get_paginated_response(serializer.data)
        return representation

    class Meta(CategorySerializer.Meta):
        fields = ["id", "name", "image", "products"]


class ProductDetailSerializer(ProductSerializer):
    """Serializer for product detail view."""

    images = ProductImageSerializer(many=True, read_only=True)
    features = ProductFeatureSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            "features",
            "ratings",
            "reviews",
            "category",
            "images",
            "is_trending",
            "is_featured",
        ]

    def to_representation(self, instance):
        """Add average rating to serialized data."""
        representation = super().to_representation(instance)

        thumbnail = instance.images.filter(is_thumbnail=True).first()
        if thumbnail:
            representation["thumbnail"] = ProductThumbnailSerializer(
                thumbnail, context=self.context
            ).data
        else:
            representation["thumbnail"] = {}

        average_rating = instance.ratings.aggregate(average_rating=Avg("rating"))[
            "average_rating"
        ]
        representation["average_rating"] = (
            average_rating if average_rating is not None else 0
        )
        representation["reviews"] = representation.get("reviews", [])

        # Add reviews count
        reviews_count = instance.reviews.count()
        representation["reviews_count"] = reviews_count

        return representation


class WeeklyDealSerializer(serializers.ModelSerializer):
    """Serializer for weekly deals."""

    product = ProductSerializer(read_only=True)

    class Meta:
        model = models.WeeklyDeal
        fields = ["id", "deal_time", "product"]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        """Add product to serialized data."""
        representation = super().to_representation(instance)

        product = ProductSerializer(instance.product, context=self.context).data
        print(product)
        representation["product"] = product

        return representation
