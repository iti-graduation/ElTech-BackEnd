# production.py
from .base import *

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Database settings for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':os.environ.get('DB_NAME'),
        'USER':os.environ.get('DB_USER'),
        'PASSWORD':os.environ.get('DB_PASS'),
        'HOST':os.environ.get('DB_HOST'),
        'PORT':os.environ.get('DB_PORT', '5432'),
    }
}

# Email backend for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yourprovider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
