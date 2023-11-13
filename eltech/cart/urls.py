"""
URL mappings for the cart app.
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from cart import views

router = DefaultRouter()
router.register('carts', views.CartViewSet)

app_name = 'cart'

urlpatterns = [
    path('', include(router.urls)),
]