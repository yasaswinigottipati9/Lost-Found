"""
Main URL Configuration for Lost & Found Smart Platform
======================================================
Student Note: This is the main URL router. It connects the project-level
URLs to the app-level URLs.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # For serving media files in development

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin panel
    path('', include('lostfound.urls')),       # Include all lostfound app URLs
    path('accounts/', include('django.contrib.auth.urls')),  # Built-in auth URLs (login/logout)
]

# Serve media files during development
# Student Note: In production, the web server (Nginx/Apache) serves media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
