"""
Django Settings for Lost & Found Smart Platform
================================================
This file contains all configuration for the Django project.
Student Note: Settings control database, installed apps, templates, etc.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-lostandfound-student-project-secret-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']  # Allow all hosts for development

# Application definition - list of all Django apps used in project
INSTALLED_APPS = [
    'django.contrib.admin',          # Django admin panel
    'django.contrib.auth',           # Authentication system
    'django.contrib.contenttypes',   # Content types framework
    'django.contrib.sessions',       # Session management
    'django.contrib.messages',       # Messaging framework
    'django.contrib.staticfiles',    # Static file management
    'lostfound',                     # Our main application
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lostandfound_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'lostfound' / 'templates'],  # Template directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lostandfound_project.wsgi.application'

# Database Configuration - MySQL
# Student Note: Install mysqlclient: pip install mysqlclient
# Create database: CREATE DATABASE lostandfound_db;
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Using MySQL
        'NAME': 'lostandfound_db',              # Database name
        'USER': 'root',                          # MySQL username
        'PASSWORD': '12345678',                  # MySQL password (change this!)
        'HOST': 'localhost',                     # Database host
        'PORT': '3306',                          # MySQL default port
    }
}

# SQLite alternative (easier for testing, comment out MySQL above and use this)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # Indian Standard Time
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'lostfound' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (User uploaded images)
# Student Note: MEDIA_URL is the URL prefix, MEDIA_ROOT is where files are stored on disk
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login/Logout redirect URLs
LOGIN_REDIRECT_URL = '/dashboard/'   # After login, go to dashboard
LOGIN_URL = '/login/'                 # If not logged in, redirect here
LOGOUT_REDIRECT_URL = '/'            # After logout, go to home
