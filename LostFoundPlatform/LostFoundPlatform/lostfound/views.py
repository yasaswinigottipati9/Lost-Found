"""
Views for Lost & Found Smart Platform
======================================
Student Note: Views handle the logic for each page/URL.
They receive HTTP requests, process data, and return HTTP responses.
Each function or class here corresponds to a page in our application.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required  # Requires user to be logged in
from django.contrib.auth.models import User
from django.contrib import messages                         # Flash messages (success/error)
from django.db.models import Q                             # For complex database queries (OR conditions)
from django.http import JsonResponse                       # For returning JSON (used in chat)
from django.views.decorators.http import require_POST     # Only allow POST requests
from django.utils import timezone

from .models import Item, ChatMessage, MatchRequest, UserProfile, ItemVerification
from .forms import (
    UserRegistrationForm, ItemForm, SearchFilterForm,
    ChatMessageForm, ItemVerificationForm, UserProfileForm
)
from .matching import find_matches_for_item                # Our custom matching logic


# ============================================================
# VIEW 1: Home Page
# ============================================================
def home(request):
    """
    Home page - shows recent lost and found items.
    Student Note: We fetch recent items using Django ORM queries.
    filter() is like SQL WHERE clause.
    """
    # Get 6 most recent lost items (approved and active only)
    recent_lost = Item.objects.filter(
        item_type='lost',
        is_approved=True,
        is_active=True
    ).order_by('-created_at')[:6]  # [:6] means LIMIT 6 in SQL

    # Get 6 most recent found items
    recent_found = Item.objects.filter(
        item_type='found',
        is_approved=True,
        is_active=True
    ).order_by('-created_at')[:6]

    # Get statistics for hero section
    total_lost = Item.objects.filter(item_type='lost', is_active=True).count()
    total_found = Item.objects.filter(item_type='found', is_active=True).count()
    total_delivered = Item.objects.filter(status='delivered', is_active=True).count()

    context = {
        'recent_lost': recent_lost,
        'recent_found': recent_found,
        'total_lost': total_lost,
        'total_found': total_found,
        'total_delivered': total_delivered,
    }
    return render(request, 'lostfound/home.html', context)


# ============================================================
# VIEW 2: User Registration
# ============================================================
def register(request):
    """
    User registration page.
    Student Note: We handle both GET and POST in the same view.
    GET: Show the empty registration form
    POST: Process the submitted form data
    """
    if request.user.is_authenticated:
        return redirect('home')  # Already logged in, go to home

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():                              # Validate all form fields
            user = form.save()                           # Save user to database
            login(request, user)                         # Log user in automatically
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()   # Empty form for GET request

    return render(request, 'registration/register.html', {'form': form})


# ============================================================
# VIEW 3: Dashboard - Universal Item Listing
# ============================================================
def dashboard(request):
    """
    Main dashboard showing all items with search and filter.
    Student Note: Q objects allow complex queries with AND/OR conditions.
    Example: Item.objects.filter(Q(title__icontains='phone') | Q(description__icontains='phone'))
    translates to SQL: WHERE title LIKE '%phone%' OR description LIKE '%phone%'
    """
    # Start with all approved, active items
    items = Item.objects.filter(is_approved=True, is_active=True)

    # Initialize search form
    form = SearchFilterForm(request.GET)  # GET because filters are in URL query params

    if form.is_valid():
        keyword = form.cleaned_data.get('keyword')
        category = form.cleaned_data.get('category')
        item_type = form.cleaned_data.get('item_type')
        location = form.cleaned_data.get('location')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        # Apply filters one by one
        if keyword:
            # Search in title, description, and location
            items = items.filter(
                Q(title__icontains=keyword) |        # icontains = case-insensitive contains
                Q(description__icontains=keyword) |
                Q(location__icontains=keyword)
            )

        if category:
            items = items.filter(category=category)

        if item_type:
            items = items.filter(item_type=item_type)

        if location:
            items = items.filter(location__icontains=location)

        if date_from:
            items = items.filter(date_reported__gte=date_from)   # gte = greater than or equal

        if date_to:
            items = items.filter(date_reported__lte=date_to)     # lte = less than or equal

    # Separate counts for dashboard tabs
    lost_count = items.filter(item_type='lost').count()
    found_count = items.filter(item_type='found').count()
    delivered_count = Item.objects.filter(status='delivered', is_active=True).count()
    pending_count = items.filter(status='pending').count()

    context = {
        'items': items.order_by('-created_at'),
        'form': form,
        'lost_count': lost_count,
        'found_count': found_count,
        'delivered_count': delivered_count,
        'pending_count': pending_count,
    }
    return render(request, 'lostfound/dashboard.html', context)


# ============================================================
# VIEW 4: Post Item (Lost or Found)
# ============================================================
@login_required  # User must be logged in to post items
def post_item(request):
    """
    Page for posting a lost or found item.
    Student Note: @login_required decorator redirects to login page
    if user is not authenticated.
    """
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)   # request.FILES handles image uploads
        if form.is_valid():
            item = form.save(commit=False)              # Don't save to DB yet
            item.user = request.user                    # Assign current user as owner
            item.save()                                  # Now save to DB

            # After saving, look for potential matches
            matches = find_matches_for_item(item)
            if matches:
                messages.info(
                    request,
                    f'Your item has been posted! We found {len(matches)} potential match(es). Check the item detail page.'
                )
            else:
                messages.success(request, 'Your item has been posted successfully!')

            return redirect('item_detail', pk=item.pk)
        else:
            messages.error(request, 'Please fill all required fields correctly.')
    else:
        # Pre-fill item_type if passed in URL (e.g., /post-item/?type=lost)
        initial = {}
        item_type = request.GET.get('type', '')
        if item_type in ['lost', 'found']:
            initial['item_type'] = item_type

        form = ItemForm(initial=initial)

    return render(request, 'lostfound/post_item.html', {'form': form})


# ============================================================
# VIEW 5: Item Detail Page
# ============================================================
def item_detail(request, pk):
    """
    Shows full details of a specific item.
    Student Note: get_object_or_404 fetches an item by primary key (id).
    If not found, it returns a 404 error page instead of crashing.
    """
    item = get_object_or_404(Item, pk=pk, is_active=True)

    # Find potential matches for this item
    potential_matches = find_matches_for_item(item)

    # Get existing match requests
    if item.item_type == 'lost':
        match_requests = MatchRequest.objects.filter(lost_item=item)
    else:
        match_requests = MatchRequest.objects.filter(found_item=item)

    # Get chat messages related to this item
    chat_messages = ChatMessage.objects.filter(item=item).order_by('timestamp')

    # Chat form for sending new messages
    chat_form = ChatMessageForm()

    # Verification info
    try:
        verification = item.verification
    except ItemVerification.DoesNotExist:
        verification = None

    context = {
        'item': item,
        'potential_matches': potential_matches,
        'match_requests': match_requests,
        'chat_messages': chat_messages,
        'chat_form': chat_form,
        'verification': verification,
    }
    return render(request, 'lostfound/item_detail.html', context)


# ============================================================
# VIEW 6: Chat System
# ============================================================
@login_required
def chat(request, receiver_id, item_id=None):
    """
    Chat page between two users about an item.
    Student Note: We load all messages between these two users.
    mark unread messages as read when receiver opens the chat.
    """
    receiver = get_object_or_404(User, pk=receiver_id)
    item = get_object_or_404(Item, pk=item_id) if item_id else None

    # Build query for messages between these two users
    messages_qs = ChatMessage.objects.filter(
        Q(sender=request.user, receiver=receiver) |  # Messages I sent
        Q(sender=receiver, receiver=request.user)     # Messages I received
    )

    if item:
        messages_qs = messages_qs.filter(item=item)  # Filter by specific item

    messages_list = messages_qs.order_by('timestamp')

    # Mark received messages as read
    ChatMessage.objects.filter(
        sender=receiver,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    # Handle sending a new message
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = receiver
            msg.item = item
            msg.save()
            return redirect('chat', receiver_id=receiver_id, item_id=item_id or 0)
    else:
        form = ChatMessageForm()

    # Get all conversations (unique users this person has chatted with)
    conversations = get_user_conversations(request.user)

    context = {
        'receiver': receiver,
        'item': item,
        'messages_list': messages_list,
        'form': form,
        'conversations': conversations,
    }
    return render(request, 'lostfound/chat.html', context)


@login_required
@require_POST
def send_message_ajax(request):
    """
    AJAX endpoint for sending messages without page reload.
    Student Note: Returns JSON data that JavaScript on the frontend uses
    to update the chat UI dynamically.
    """
    import json
    data = json.loads(request.body)

    receiver_id = data.get('receiver_id')
    message_text = data.get('message')
    item_id = data.get('item_id')

    if not receiver_id or not message_text:
        return JsonResponse({'error': 'Missing data'}, status=400)

    receiver = get_object_or_404(User, pk=receiver_id)
    item = Item.objects.filter(pk=item_id).first() if item_id else None

    msg = ChatMessage.objects.create(
        sender=request.user,
        receiver=receiver,
        item=item,
        message=message_text
    )

    return JsonResponse({
        'success': True,
        'message_id': msg.id,
        'sender': msg.sender.username,
        'message': msg.message,
        'timestamp': msg.timestamp.strftime('%d %b %Y, %I:%M %p'),
    })


def get_user_conversations(user):
    """Helper function to get list of users someone has chatted with"""
    # Get all unique users from sent/received messages
    sent_to = ChatMessage.objects.filter(sender=user).values_list('receiver', flat=True).distinct()
    received_from = ChatMessage.objects.filter(receiver=user).values_list('sender', flat=True).distinct()

    # Combine unique user IDs
    user_ids = set(list(sent_to) + list(received_from))
    return User.objects.filter(pk__in=user_ids)


# ============================================================
# VIEW 7: User Dashboard (Personal)
# ============================================================
@login_required
def user_dashboard(request):
    """
    Personal dashboard for the logged-in user.
    Shows their posted items, matches, and chat history.
    """
    user = request.user

    # Get current user's items
    my_items = Item.objects.filter(user=user, is_active=True).order_by('-created_at')

    # Get match requests related to user's items
    my_lost_items = my_items.filter(item_type='lost')
    my_found_items = my_items.filter(item_type='found')

    # Unread message count
    unread_messages = ChatMessage.objects.filter(receiver=user, is_read=False).count()

    # Recent conversations
    conversations = get_user_conversations(user)

    context = {
        'my_items': my_items,
        'my_lost_items': my_lost_items,
        'my_found_items': my_found_items,
        'lost_count': my_lost_items.count(),
        'found_count': my_found_items.count(),
        'delivered_count': my_items.filter(status='delivered').count(),
        'unread_messages': unread_messages,
        'conversations': conversations,
    }
    return render(request, 'lostfound/user_dashboard.html', context)


# ============================================================
# VIEW 8: Item Verification
# ============================================================
@login_required
def verify_item(request, pk):
    """
    Verification page before marking item as delivered.
    Student Note: Only the finder (item poster) can verify an item.
    """
    item = get_object_or_404(Item, pk=pk)

    # Only item owner can verify
    if item.user != request.user:
        messages.error(request, 'You can only verify items you posted.')
        return redirect('item_detail', pk=pk)

    if request.method == 'POST':
        form = ItemVerificationForm(request.POST)
        if form.is_valid():
            verification, created = ItemVerification.objects.get_or_create(item=item)
            verification.verification_detail = form.cleaned_data['verification_detail']
            verification.notes = form.cleaned_data.get('notes', '')
            verification.is_verified = True
            verification.verified_by = request.user
            verification.verified_at = timezone.now()
            verification.save()

            # Update item status to delivered
            item.status = 'delivered'
            item.save()

            messages.success(request, f'Item "{item.title}" has been marked as delivered!')
            return redirect('user_dashboard')
    else:
        form = ItemVerificationForm()

    return render(request, 'lostfound/verify_item.html', {'item': item, 'form': form})


# ============================================================
# VIEW 9: Edit Item
# ============================================================
@login_required
def edit_item(request, pk):
    """Edit an existing item posting"""
    item = get_object_or_404(Item, pk=pk, user=request.user)  # Only owner can edit

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)  # instance= for editing
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('item_detail', pk=pk)
    else:
        form = ItemForm(instance=item)

    return render(request, 'lostfound/post_item.html', {'form': form, 'editing': True, 'item': item})


# ============================================================
# VIEW 10: Delete Item
# ============================================================
@login_required
def delete_item(request, pk):
    """Soft delete an item (mark as inactive instead of actually deleting)"""
    item = get_object_or_404(Item, pk=pk, user=request.user)

    if request.method == 'POST':
        item.is_active = False   # Soft delete - don't actually remove from DB
        item.save()
        messages.success(request, f'Item "{item.title}" has been removed.')
        return redirect('user_dashboard')

    return render(request, 'lostfound/confirm_delete.html', {'item': item})


# ============================================================
# VIEW 11: User Profile
# ============================================================
@login_required
def profile(request):
    """View and edit user profile"""
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'lostfound/profile.html', {'form': form, 'user_profile': user_profile})


# ============================================================
# VIEW 12: Create Match Request
# ============================================================
@login_required
def create_match(request, lost_item_id, found_item_id):
    """Create a match request between a lost and found item"""
    lost_item = get_object_or_404(Item, pk=lost_item_id, item_type='lost')
    found_item = get_object_or_404(Item, pk=found_item_id, item_type='found')

    # Check if match already exists
    match, created = MatchRequest.objects.get_or_create(
        lost_item=lost_item,
        found_item=found_item
    )

    if created:
        # Update both item statuses
        lost_item.status = 'matched'
        lost_item.save()
        found_item.status = 'matched'
        found_item.save()
        messages.success(request, 'Match request created! Contact the other user to confirm.')
    else:
        messages.info(request, 'A match request already exists for these items.')

    return redirect('item_detail', pk=lost_item_id)
