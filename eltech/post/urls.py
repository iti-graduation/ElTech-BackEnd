"""
URL mappings for the post app.
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from post import views

# Create a router for the posts
router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')


app_name = 'post'


urlpatterns = [
    path('', include(router.urls)),
    path('posts/<int:pk>/comments/', views.PostViewSet.as_view({'post': 'comments'}), name='post-comments'),
    ]