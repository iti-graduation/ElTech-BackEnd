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

app_name = 'product'

urlpatterns = [
    path('', include(router.urls)),
    # path('weekly-deal/', views.WeeklyDealView.as_view(), name='weekly-deal'),
    path('products/<int:pk>/reviews/', views.ProductViewSet.as_view({'post': 'reviews'}), name='product-reviews'),
    path('products/<int:pk>/ratings/', views.ProductViewSet.as_view({'post': 'ratings'}), name='product-ratings'),
    path('products/<int:pk>/reviews/<int:review_id>/', views.ProductViewSet.as_view({'delete': 'delete_review'}),
         name='product-review-delete'),
]
