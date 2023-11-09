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


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""

    class Meta:
        model = models.Category
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""

    class Meta:
        model = models.Product
        fields = ['id', 'name', 'price', 'is_hot', 'is_on_sale', 'sale_amount']
        read_only_fields = ['id']


class ProductDetailSerializer(ProductSerializer):
    """Serializer for product detail view."""
    features = ProductFeatureSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            'description', 'stock', 'features', 'ratings', 'reviews', 'category'
        ]

    def to_representation(self, instance):
        """Add average rating to serialized data."""
        representation = super().to_representation(instance)
        average_rating = instance.rating_set.aggregate(
            average_rating=Avg('rating')
        )['average_rating']
        representation['average_rating'] = average_rating \
            if average_rating is not None else 0
        representation['reviews'] = representation.get('reviews', [])
        return representation


class WeeklyDealSerializer(serializers.ModelSerializer):
    """Serializer for weekly deals."""
    product = ProductSerializer(read_only=True)

    class Meta:
        model = models.WeeklyDeal
        fields = ['id', 'deal_time', 'product']
        read_only_fields = ['id']
