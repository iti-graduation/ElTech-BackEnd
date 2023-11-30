"""
Views for the post APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework import views, viewsets, mixins, status

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter



from django.db.models import Q

from core.models import Comment , Post

from post.serializers import *

    
class PostPagination(PageNumberPagination):
    page_size = 2  # Set the number of posts per page
    page_size_query_param = 'page_size'  # Customize query parameter for page size
    max_page_size = 1000  # Set a maximum page size if needed

@extend_schema_view(
    list=extend_schema(parameters=[
        OpenApiParameter(
                "category_id",
                OpenApiTypes.INT,
                description="Search term for filtering posts by Category.",
            ),
            OpenApiParameter(
                "user_id",
                OpenApiTypes.INT,
                description="Search term for filtering posts by User.",
            ),
            OpenApiParameter(
                "search",
                OpenApiTypes.STR,
                description="Search term for filtering posts by title or content.",
            ),
    ]),
    description="List and create posts.",
    responses={200: PostSerializer(many=True)},
)
class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all().order_by('-created_at')
    pagination_class = PostPagination 
    authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    # ordering_fields = ['created_at','user_id']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = []
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


    def get_queryset(self):
        queryset = self.queryset

        # Filter posts based on Search
        query = self.request.query_params.get("search")
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))

        # Filter posts based on category
        category_id = self.request.query_params.get('category_id', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Filter posts based on user
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    @extend_schema(request=CommentSerializer,description="List and create comments.", responses={200: CommentSerializer(many=True)})
    @action(detail=True, methods=['post', 'get'])
    def comments(self, request, pk=None):
        """Create or retrieve comments for a post."""
        post = self.get_object()

        if request.method == 'POST':
            serializer = CommentSerializer(data=request.data)
            # Add authentication and permission checks
            self.check_object_permissions(request, post)

            if serializer.is_valid():
                serializer.save(user=request.user, post=post)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'GET':
            comments = post.comments.all()  # Assuming you have a related_name='comments' in your Post model
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    @extend_schema(request=CommentSerializer,description="List and create comments.", responses={200: CommentSerializer(many=True)})
    @action(detail=True, methods=['get'], url_path='comments/(?P<comment_id>[^/.]+)')
    def get_comment(self, request, pk=None, comment_id=None):
        """Retrieve a comment by ID."""
        post = self.get_object()

        try:
            comment = Comment.objects.get(id=comment_id, post=post)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(request=CommentSerializer,description="List and create comments.", responses={200: CommentSerializer(many=True)})
    @action(detail=True, methods=['patch'], url_path='comments/(?P<comment_id>[^/.]+)')
    def update_comment(self, request, pk=None, comment_id=None):
        """Update a comment by ID."""
        post = self.get_object()

        try:
            comment = Comment.objects.get(id=comment_id, post=post)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Check if the user is the owner of the comment
        if comment.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(request=CommentSerializer,description="List and create comments.", responses={200: CommentSerializer(many=True)})
    @action(detail=True, methods=['delete'], url_path='comments/(?P<comment_id>[^/.]+)')
    def delete_comment(self, request, pk=None, comment_id=None):
        """Delete a review for a product."""
        post = self.get_object()

        try:
            comment = Comment.objects.get(id=comment_id, post=post)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Check if the user is the owner of the review
        if comment.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()