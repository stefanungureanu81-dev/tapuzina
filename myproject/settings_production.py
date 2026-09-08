from .settings import *
import os

DEBUG = False

ALLOWED_HOSTS = ['tapuzina.ro', 'www.tapuzina.ro', 'mgh-web9.maghost.ro']

# Database - MySQL pentru MagHost
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tapuzina_tapuzina_db',
        'USER': 'tapuzina_admin',
        'PASSWORD': 'Jag2867XY@2026',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Static files
STATIC_ROOT = '/home/tapuzina/public_html/staticfiles'
MEDIA_ROOT = '/home/tapuzina/public_html/media'

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email
EMAIL_HOST = 'mail.tapuzina.ro'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'orar@tapuzina.ro'
EMAIL_HOST_PASSWORD = 'Jag2867XY@2026'
DEFAULT_FROM_EMAIL = 'orar@tapuzina.ro'

SITE_URL = 'https://tapuzina.ro'