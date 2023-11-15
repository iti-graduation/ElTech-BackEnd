"""
Serializers for product APIs
"""
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from django.db.models import Avg

from core import models


class UserSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    class Meta:
        model = models.User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile_picture']
        read_only_fields = ['id', 'email', 'first_name', 'last_name', 'profile_picture']


class RatingSerializer(serializers.ModelSerializer):
    """Serializer for ratings."""

    class Meta:
        model = models.Rating
        fields = ['id', 'rating', 'user']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = models.Review
        fields = ['id', 'content', 'created_at', 'updated_at', 'user']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductFeatureSerializer(serializers.ModelSerializer):
    """Serializer for product features."""

    class Meta:
        model = models.ProductFeature
        fields = ['id', 'feature']
        read_only_fields = ['id']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""

    class Meta:
        model = models.ProductImage
        fields = ['id', 'image']
        read_only_fields = ['id', 'image']


class ProductThumbnailSerializer(serializers.ModelSerializer):
    """Serializer for product thumbnail."""

    class Meta:
        model = models.ProductImage
        fields = ['image']
        read_only_fields = ['image']

    # def to_representation(self, instance):
    #     """Only return the image if it is a thumbnail."""
    #     if instance.is_thumbnail:
    #         return {'image': self.context['request'].build_absolute_uri(instance.image.url)}
    #     return {}
    def to_representation(self, instance):
        """Only return the image if it is a thumbnail."""
        request = self.context.get('request')
        if request and instance.is_thumbnail:
            return {'image': request.build_absolute_uri(instance.image.url)}
        return {}


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""
    thumbnail = ProductThumbnailSerializer(read_only=True)

    class Meta:
        model = models.Product
        fields = ['id', 'name', 'price', 'is_hot', 'is_on_sale',
                  'sale_amount', 'thumbnail', 'description', 'stock']
        read_only_fields = ['id']

    def to_representation(self, instance):
        """Add thumbnail to serialized data."""
        representation = super().to_representation(instance)

        thumbnail = instance.images.filter(is_thumbnail=True).first()
        if thumbnail:
            representation['thumbnail'] = ProductThumbnailSerializer(thumbnail, context=self.context).data
        else:
            representation['thumbnail'] = {}

        return representation


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""

    class Meta:
        model = models.Category
        fields = ['id', 'name', 'image']
        read_only_fields = ['id']

class CustomPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return {
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        }

# class CategoryDetailSerializer(CategorySerializer):
#     """Serializer for category detail view."""
#     products = ProductSerializer(many=True, read_only=True)

#     class Meta(CategorySerializer.Meta):
#         fields = ['id', 'name', 'products']

class CategoryDetailSerializer(CategorySerializer):
    """Serializer for category detail view."""

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        paginator = CustomPagination()
        paginator.page_size = 5  # Set the number of items per page here

        # Apply the pagination
        products = paginator.paginate_queryset(instance.products.all(), request)
        serializer = ProductSerializer(products, many=True, context={'request': request})

        # Add the paginated results to the representation
        representation['products'] = paginator.get_paginated_response(serializer.data)
        return representation

    class Meta(CategorySerializer.Meta):
        fields = ['id', 'name', 'image', 'products']


class ProductDetailSerializer(ProductSerializer):
    """Serializer for product detail view."""
    images = ProductImageSerializer(many=True, read_only=True)
    features = ProductFeatureSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            'features', 'ratings', 'reviews',
            'category', 'images'
        ]

    def to_representation(self, instance):
        """Add average rating to serialized data."""
        representation = super().to_representation(instance)

        thumbnail = instance.images.filter(is_thumbnail=True).first()
        if thumbnail:
            representation['thumbnail'] = ProductThumbnailSerializer(thumbnail, context=self.context).data
        else:
            representation['thumbnail'] = {}

        # average_rating = instance.rating_set.aggregate(
        #     average_rating=Avg('rating')
        # )['average_rating']
        average_rating = instance.ratings.aggregate(
            average_rating=Avg('rating')
        )['average_rating']
        representation['average_rating'] = average_rating \
            if average_rating is not None else 0
        representation['reviews'] = representation.get('reviews', [])

        # Add reviews count
        reviews_count = instance.reviews.count()
        representation['reviews_count'] = reviews_count

        return representation


# class WeeklyDealSerializer(serializers.ModelSerializer):
#     """Serializer for weekly deals."""
#     product = ProductSerializer(read_only=True)
#
#     class Meta:
#         model = models.WeeklyDeal
#         fields = ['id', 'deal_time', 'product']
#         read_only_fields = ['id']

class WeeklyDealSerializer(serializers.ModelSerializer):
    """Serializer for weekly deals."""
    product = ProductSerializer(read_only=True)

    class Meta:
        model = models.WeeklyDeal
        fields = ['id', 'deal_time', 'product']
        read_only_fields = ['id']

    def to_representation(self, instance):
        """Add product to serialized data."""
        representation = super().to_representation(instance)

        product = ProductSerializer(instance.product, context=self.context).data
        print(product)
        representation['product'] = product

        return representation


