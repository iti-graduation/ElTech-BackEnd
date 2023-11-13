"""
Serializers for product APIs
"""
from rest_framework import serializers

from django.db.models import Avg

from core import models


class UserSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    class Meta:
        model = models.User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'email', 'first_name', 'last_name']


class RatingSerializer(serializers.ModelSerializer):
    """Serializer for ratings."""

    class Meta:
        model = models.Rating
        fields = ['id', 'rating']
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
        fields = ['image']
        read_only_fields = ['image']


class ProductThumbnailSerializer(serializers.ModelSerializer):
    """Serializer for product thumbnail."""

    class Meta:
        model = models.ProductImage
        fields = ['image']
        read_only_fields = ['image']

    def to_representation(self, instance):
        """Only return the image if it is a thumbnail."""
        if instance.is_thumbnail:
            return {'image': self.context['request'].build_absolute_uri(instance.image.url)}
        return {}


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""
    thumbnail = ProductThumbnailSerializer(read_only=True)

    class Meta:
        model = models.Product
        fields = ['id', 'name', 'price', 'is_hot', 'is_on_sale',
                  'sale_amount', 'thumbnail']
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


class CategoryDetailSerializer(CategorySerializer):
    """Serializer for category detail view."""
    products = ProductSerializer(many=True, read_only=True)

    class Meta(CategorySerializer.Meta):
        fields = ['id', 'name', 'products']


class ProductDetailSerializer(ProductSerializer):
    """Serializer for product detail view."""
    images = ProductImageSerializer(many=True, read_only=True)
    features = ProductFeatureSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            'description', 'stock', 'features', 'ratings', 'reviews',
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

        average_rating = instance.rating_set.aggregate(
            average_rating=Avg('rating')
        )['average_rating']
        representation['average_rating'] = average_rating \
            if average_rating is not None else 0
        representation['reviews'] = representation.get('reviews', [])

        # Add reviews count
        reviews_count = instance.reviews.count()
        representation['reviews_count'] = reviews_count

        return representation


class WeeklyDealSerializer(serializers.ModelSerializer):
    """Serializer for weekly deals."""
    product = ProductSerializer(read_only=True)

    class Meta:
        model = models.WeeklyDeal
        fields = ['id', 'deal_time', 'product']
        read_only_fields = ['id']
