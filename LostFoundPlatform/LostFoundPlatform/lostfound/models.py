"""
Models for Lost & Found Smart Platform
=======================================
Student Note: Models are Python classes that map to database tables.
Each attribute in the class becomes a column in the database table.
Django automatically handles SQL queries through the ORM (Object Relational Mapper).
"""

from django.db import models
from django.contrib.auth.models import User  # Import Django's built-in User model
from django.utils import timezone


# ============================================================
# ITEM CATEGORIES - defines what kind of item it is
# ============================================================
CATEGORY_CHOICES = [
    ('electronics', 'Electronics'),           # Phones, laptops, etc.
    ('documents', 'Documents'),               # ID cards, certificates, etc.
    ('vehicles', 'Vehicles'),                 # Bikes, cars, etc.
    ('clothing', 'Clothing & Accessories'),   # Bags, wallets, etc.
    ('keys', 'Keys'),                         # House/vehicle keys
    ('jewelry', 'Jewelry'),                   # Rings, necklaces, etc.
    ('animals', 'Animals/Pets'),              # Lost/found pets
    ('books', 'Books & Stationery'),          # Academic materials
    ('sports', 'Sports Equipment'),           # Sports items
    ('other', 'Other'),                       # Anything else
]

# ============================================================
# ITEM TYPE - Whether item is Lost or Found
# ============================================================
ITEM_TYPE_CHOICES = [
    ('lost', 'Lost'),
    ('found', 'Found'),
]

# ============================================================
# ITEM STATUS - Current status of the item
# ============================================================
STATUS_CHOICES = [
    ('pending', 'Pending'),                   # Just posted, not verified
    ('matched', 'Matched'),                   # A match has been found
    ('pending_verification', 'Pending Verification'),  # Match found, waiting confirmation
    ('delivered', 'Delivered'),               # Item returned to owner
]


# ============================================================
# MODEL 1: UserProfile - Extra info for each user
# ============================================================
class UserProfile(models.Model):
    """
    Extends Django's built-in User model with extra fields.
    Student Note: OneToOneField means each User has exactly one Profile.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)       # Optional phone number
    address = models.TextField(blank=True)                     # Optional address
    profile_photo = models.ImageField(
        upload_to='profile_photos/',                           # Stored in media/profile_photos/
        blank=True,
        null=True
    )
    bio = models.TextField(blank=True)                         # Short bio
    created_at = models.DateTimeField(auto_now_add=True)       # When profile was created

    def __str__(self):
        # String representation shown in admin panel
        return f"Profile of {self.user.username}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


# ============================================================
# MODEL 2: Item - Main model for lost/found items
# ============================================================
class Item(models.Model):
    """
    Main model to store both Lost and Found items.
    Student Note: ForeignKey creates a many-to-one relationship.
    One user can post many items.
    """
    # Who posted this item
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,    # If user deleted, delete their items too
        related_name='items'
    )

    # Basic item information
    title = models.CharField(max_length=200)                   # Item name/title
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    description = models.TextField()                           # Detailed description
    item_type = models.CharField(
        max_length=10,
        choices=ITEM_TYPE_CHOICES                              # Lost or Found
    )

    # Location information
    location = models.CharField(max_length=300)                # Where lost/found
    location_detail = models.TextField(blank=True)             # More location details

    # Date information
    date_reported = models.DateField()                         # Date item was lost/found
    created_at = models.DateTimeField(auto_now_add=True)       # When post was created
    updated_at = models.DateTimeField(auto_now=True)           # When post was last updated

    # Image upload
    image = models.ImageField(
        upload_to='items/',                                    # Stored in media/items/
        blank=True,
        null=True
    )

    # Status tracking
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending'                                      # New items start as pending
    )

    # Contact information (optional - user can choose to show/hide)
    contact_phone = models.CharField(max_length=15, blank=True)
    contact_email = models.EmailField(blank=True)

    # Admin approval flag
    is_approved = models.BooleanField(default=True)            # Admin can approve/reject
    is_active = models.BooleanField(default=True)              # Soft delete flag

    def __str__(self):
        return f"[{self.item_type.upper()}] {self.title} - {self.location}"

    def get_status_badge_color(self):
        """Returns Bootstrap badge color based on status"""
        colors = {
            'pending': 'warning',
            'matched': 'info',
            'pending_verification': 'primary',
            'delivered': 'success',
        }
        return colors.get(self.status, 'secondary')

    def get_type_badge_color(self):
        """Returns Bootstrap badge color based on item type"""
        return 'danger' if self.item_type == 'lost' else 'success'

    class Meta:
        ordering = ['-created_at']                             # Newest items first
        verbose_name = "Item"
        verbose_name_plural = "Items"


# ============================================================
# MODEL 3: MatchRequest - Links lost item with found item
# ============================================================
class MatchRequest(models.Model):
    """
    When a lost item matches a found item, a MatchRequest is created.
    Student Note: Two ForeignKeys linking to the same model (Item).
    One is the lost item, one is the found item.
    """
    MATCH_STATUS = [
        ('pending', 'Pending'),           # Match suggested, not yet accepted
        ('accepted', 'Accepted'),         # Both parties accepted the match
        ('rejected', 'Rejected'),         # Match was rejected
        ('completed', 'Completed'),       # Item delivered successfully
    ]

    lost_item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='lost_matches'       # Access via: item.lost_matches.all()
    )
    found_item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='found_matches'      # Access via: item.found_matches.all()
    )
    status = models.CharField(max_length=20, choices=MATCH_STATUS, default='pending')
    match_score = models.FloatField(default=0.0)               # How close is the match (0-100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)                       # Admin/system notes

    def __str__(self):
        return f"Match: {self.lost_item.title} <-> {self.found_item.title} [{self.status}]"

    class Meta:
        verbose_name = "Match Request"
        verbose_name_plural = "Match Requests"
        unique_together = ['lost_item', 'found_item']          # Can't have duplicate matches


# ============================================================
# MODEL 4: ChatMessage - Messages between users
# ============================================================
class ChatMessage(models.Model):
    """
    Chat messages between users about a specific item.
    Student Note: sender and receiver are both ForeignKeys to User.
    This creates a simple direct messaging system.
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'      # Access via: user.sent_messages.all()
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'  # Access via: user.received_messages.all()
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='chat_messages',     # Messages about a specific item
        null=True,
        blank=True
    )
    message = models.TextField()          # The actual message content
    timestamp = models.DateTimeField(auto_now_add=True)        # When message was sent
    is_read = models.BooleanField(default=False)               # Has receiver read it?

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.message[:50]}"

    class Meta:
        ordering = ['timestamp']          # Oldest messages first (chronological order)
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"


# ============================================================
# MODEL 5: ItemVerification - For verifying ownership
# ============================================================
class ItemVerification(models.Model):
    """
    Stores verification details when an item is being returned.
    The owner must provide proof to claim the item.
    """
    item = models.OneToOneField(
        Item,
        on_delete=models.CASCADE,
        related_name='verification'
    )
    verification_detail = models.TextField()    # IMEI, document number, etc.
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='verifications_done'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Verification for: {self.item.title}"

    class Meta:
        verbose_name = "Item Verification"
        verbose_name_plural = "Item Verifications"
