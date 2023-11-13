"""
Views for the order APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Product,
    Order,
    OrderProduct,
)
from order import serializers


class OrderViewSet(viewsets.ModelViewSet):
    """View for manage order APIs."""

    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve orders for authenticated user."""
        return self.queryset.filter(user=self.request.user)

    # def get_serializer_class(self):
    #     """Return the serializer class for request."""
    #     if self.action == "list":
    #         return serializers.RecipeSerializer
    #     elif self.action == "upload_image":
    #         return serializers.RecipeImageSerializer
    #
    #     return self.serializer_class

    def perform_create(self, serializer):
        """Create a new order."""
        serializer.save(user=self.request.user)

# class OrderProductViewSet(
#     mixins.DestroyModelMixin,
#     mixins.UpdateModelMixin,
#     mixins.ListModelMixin,
#     viewsets.GenericViewSet,
# ):
#     """Base viewset for recipe attributes."""
#
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         """Filter queryset for authenticated user."""
#         assigned_only = bool(int(self.request.query_params.get("assigned_only", 0)))
#         queryset = self.queryset
#
#         if assigned_only:
#             queryset = queryset.filter(recipe__isnull=False)
#
#         return queryset.filter(user=self.request.user).order_by("-name").distinct()
#
# class IngredientViewSet(BaseRecipeAttributeViewSet):
#     """Views for manage ingredients APIs."""
#
#     serializer_class = serializers.IngredientSerializer
#     queryset = Ingredient.objects.all()
