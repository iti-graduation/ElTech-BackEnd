# myapp/urls.py
from django.urls import path
from .views import create_checkout_session

urlpatterns = [
    path('online-payment/', create_checkout_session,
         name='online-payment'),
    # Add other URLs as needed
]
