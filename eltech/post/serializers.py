"""
Serializers for product APIs
"""
from rest_framework import serializers

from core import models

class UserSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    class Meta:
        model = models.User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile_picture']
        read_only_fields = ['id', 'email', 'first_name', 'last_name', 'profile_picture']
        
class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""

    class Meta:
        model = models.Category
        fields = ['id', 'name', 'image']
        read_only_fields = ['id']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) 
    class Meta:
        model = models.Comment
        # fields = '__all__'
        fields = ['id', 'content', 'created_at', 'parent', 'post', 'user']
        read_only_fields = ['id', 'created_at', 'updated_at']

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) 
    category = serializers.PrimaryKeyRelatedField(queryset=models.Category.objects.all())
    class Meta:
        model = models.Post
        fields = ['id', 'category', 'title', 'content', 'image','user','created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
