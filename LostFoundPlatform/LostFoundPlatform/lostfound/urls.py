"""
URL Configuration for Lost & Found App
=======================================
Student Note: URL patterns map URLs to view functions.
path('url/', view_function, name='url_name')
The 'name' allows you to use {% url 'url_name' %} in templates.
"""

from django.urls import path
from . import views

# URL patterns - each line maps a URL to a view function
urlpatterns = [
    # -------------------------------------------------------
    # PUBLIC PAGES (no login required)
    # -------------------------------------------------------
    path('', views.home, name='home'),                              # Home: /
    path('dashboard/', views.dashboard, name='dashboard'),          # Dashboard: /dashboard/
    path('item/<int:pk>/', views.item_detail, name='item_detail'),  # Item detail: /item/5/
    path('register/', views.register, name='register'),             # Register: /register/

    # -------------------------------------------------------
    # PROTECTED PAGES (login required)
    # -------------------------------------------------------
    path('post-item/', views.post_item, name='post_item'),          # Post new item: /post-item/
    path('item/<int:pk>/edit/', views.edit_item, name='edit_item'), # Edit item: /item/5/edit/
    path('item/<int:pk>/delete/', views.delete_item, name='delete_item'),  # Delete item
    path('item/<int:pk>/verify/', views.verify_item, name='verify_item'),  # Verify item

    # -------------------------------------------------------
    # CHAT SYSTEM
    # -------------------------------------------------------
    path('chat/<int:receiver_id>/', views.chat, name='chat'),                            # Chat with user
    path('chat/<int:receiver_id>/<int:item_id>/', views.chat, name='chat_with_item'),   # Chat about specific item
    path('chat/send/', views.send_message_ajax, name='send_message_ajax'),               # AJAX send message

    # -------------------------------------------------------
    # USER DASHBOARD & PROFILE
    # -------------------------------------------------------
    path('my-dashboard/', views.user_dashboard, name='user_dashboard'),  # Personal dashboard
    path('profile/', views.profile, name='profile'),                      # User profile

    # -------------------------------------------------------
    # MATCHING SYSTEM
    # -------------------------------------------------------
    path('match/<int:lost_item_id>/<int:found_item_id>/', views.create_match, name='create_match'),
]
