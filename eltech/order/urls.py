"""
URL mappings for the cart app.
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from order import views

router = DefaultRouter()
router.register('orders', views.OrderViewSet)

app_name = 'order'

urlpatterns = [
    path('', include(router.urls)),
    path('ordersList/', views.OrderListView.as_view(), name='order-list'),
    path('order-details/<int:pk>', views.OrderRetrieveView.as_view(), name='order-details'),
]
