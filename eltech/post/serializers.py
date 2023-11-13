"""
Serializers for product APIs
"""
from rest_framework import serializers

from core import models


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']