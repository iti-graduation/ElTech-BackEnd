# development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Development specific apps if any
INSTALLED_APPS += [
    # ...
]

MIDDLEWARE += [
    # ...
]

# Database settings for development might use SQLite or your local Postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':os.environ.get('DB_NAME'),
        'USER':os.environ.get('DB_USER'),
        'PASSWORD':os.environ.get('DB_PASS'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT':os.environ.get('DB_PORT', '5432'),
    }
}

# Email backend for development
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_PORT = 587
EMAIL_FROM = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

# ...
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
