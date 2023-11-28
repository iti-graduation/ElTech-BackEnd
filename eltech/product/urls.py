"""
URL mappings for the product app.
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from product import views

router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('categories', views.CategoryViewSet)
router.register('weekly-deal', views.WeeklyDealViewSet)
router.register('features', views.ProductFeatureViewSet)
router.register('images', views.ProductImageViewSet)

app_name = 'product'

urlpatterns = [
    path('', include(router.urls)),
    path('products/<int:pk>/reviews/', views.ProductViewSet.as_view({'post': 'reviews'}), name='product-reviews'),
    path('products/<int:pk>/ratings/', views.ProductViewSet.as_view({'post': 'ratings'}), name='product-ratings'),
    path('products/<int:pk>/upload_image/', views.ProductViewSet.as_view({'post': 'upload_image'}), name='product-upload-image'),
    path('products/<int:pk>/reviews/<int:review_id>/', views.ProductViewSet.as_view({'delete': 'delete_review'}),
        name='product-review-delete'),
    path('weekly-deal/', views.WeeklyDealViewSet.as_view({'patch': 'update'}), name='weekly-deal-update'),
]
