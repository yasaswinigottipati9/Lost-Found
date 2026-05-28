"""
Admin Configuration for Lost & Found Smart Platform
====================================================
Student Note: Django's admin panel is a powerful built-in feature.
By registering models here, they become manageable through /admin/ URL.
"""

from django.contrib import admin
from .models import Item, ChatMessage, MatchRequest, UserProfile, ItemVerification


# ============================================================
# ITEM ADMIN - Customize how Items appear in admin
# ============================================================
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Custom admin view for Item model"""

    # Columns shown in the list view
    list_display = ['title', 'user', 'item_type', 'category', 'location', 'status', 'is_approved', 'created_at']

    # Filters shown in sidebar
    list_filter = ['item_type', 'category', 'status', 'is_approved', 'is_active', 'created_at']

    # Search in these fields
    search_fields = ['title', 'description', 'location', 'user__username']

    # Make these fields editable directly in list view
    list_editable = ['is_approved', 'status']

    # Date hierarchy navigation
    date_hierarchy = 'created_at'

    # Default ordering
    ordering = ['-created_at']

    # Fields shown in detail view
    fieldsets = [
        ('Item Information', {
            'fields': ['title', 'category', 'description', 'item_type', 'image']
        }),
        ('Location & Date', {
            'fields': ['location', 'location_detail', 'date_reported']
        }),
        ('Contact Information', {
            'fields': ['contact_phone', 'contact_email'],
            'classes': ['collapse']  # Collapsed by default
        }),
        ('Status & Approval', {
            'fields': ['status', 'is_approved', 'is_active']
        }),
    ]

    # Add approval/rejection actions
    actions = ['approve_items', 'reject_items', 'mark_delivered']

    def approve_items(self, request, queryset):
        """Admin action to approve multiple items at once"""
        count = queryset.update(is_approved=True)
        self.message_user(request, f'{count} items approved successfully.')
    approve_items.short_description = 'Approve selected items'

    def reject_items(self, request, queryset):
        """Admin action to reject (hide) items"""
        count = queryset.update(is_approved=False)
        self.message_user(request, f'{count} items rejected.')
    reject_items.short_description = 'Reject selected items'

    def mark_delivered(self, request, queryset):
        """Admin action to mark items as delivered"""
        count = queryset.update(status='delivered')
        self.message_user(request, f'{count} items marked as delivered.')
    mark_delivered.short_description = 'Mark as Delivered'


# ============================================================
# USER PROFILE ADMIN
# ============================================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']


# ============================================================
# CHAT MESSAGE ADMIN
# ============================================================
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'item', 'message_preview', 'timestamp', 'is_read']
    list_filter = ['is_read', 'timestamp']
    search_fields = ['sender__username', 'receiver__username', 'message']

    def message_preview(self, obj):
        """Show only first 50 characters of message"""
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'


# ============================================================
# MATCH REQUEST ADMIN
# ============================================================
@admin.register(MatchRequest)
class MatchRequestAdmin(admin.ModelAdmin):
    list_display = ['lost_item', 'found_item', 'match_score', 'status', 'created_at']
    list_filter = ['status']
    list_editable = ['status']


# ============================================================
# ITEM VERIFICATION ADMIN
# ============================================================
@admin.register(ItemVerification)
class ItemVerificationAdmin(admin.ModelAdmin):
    list_display = ['item', 'is_verified', 'verified_by', 'verified_at']
    list_filter = ['is_verified']


# Customize Admin Site Header
admin.site.site_header = "Lost & Found Admin Panel"
admin.site.site_title = "Lost & Found Admin"
admin.site.index_title = "Welcome to Lost & Found Platform Admin"
