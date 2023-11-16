"""
Serializers for product APIs
"""
from rest_framework import serializers

from core import models

class UserSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    class Meta:
        model = models.User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'email', 'first_name', 'last_name']
        
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
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) 
    category = CategorySerializer(read_only=True)  
    class Meta:
        model = models.Post
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']