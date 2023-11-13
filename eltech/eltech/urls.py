"""
URL configuration for eltech project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # just for testing the api health
    path('api/health-check/', core_views.health_check, name='health-check'),

    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/',
         SpectacularSwaggerView.as_view(url_name='api-schema'),
         name='api-docs'
         ),

    path('api/accounts/', include('accounts.urls')),
    path('api/product/', include('product.urls')),
    path('api/post/', include('post.urls')),
    path('api/favorite/', include('favorite.urls')),
    path('api/service/', include('service.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/order/', include('order.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
