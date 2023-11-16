from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('verify-email/<uidb64>/<token>/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/', views.UnSubscribeView.as_view(), name='unsubscribe'),
]
