from rest_framework import serializers
from core.models import Favorite
from rest_framework.exceptions import ValidationError


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product']
        read_only_fields = ['user']
