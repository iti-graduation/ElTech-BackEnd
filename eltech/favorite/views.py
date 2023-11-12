from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Favorite
from .serializers import FavoriteSerializer
from favorite import serializers


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data['product']

        existing_favorite = Favorite.objects.filter(user=user, product=product)

        if existing_favorite.exists():
            raise serializers.ValidationError(
                "This user have this product already in favorites.")
        else:
            serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
