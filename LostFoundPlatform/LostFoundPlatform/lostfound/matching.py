"""
Item Matching Logic for Lost & Found Smart Platform
=====================================================
Student Note: This module contains the algorithm that compares
lost items with found items to find potential matches.

The matching algorithm considers:
1. Same category (most important - 40 points)
2. Similar location (30 points)
3. Similar description keywords (20 points)
4. Date proximity (10 points)

A match score >= 40 is considered a potential match.
"""

from .models import Item
import re


def calculate_match_score(lost_item, found_item):
    """
    Calculate how closely a lost item matches a found item.
    Returns a score from 0 to 100.
    Higher score = better match.
    
    Student Note: This is a basic scoring algorithm.
    Real-world systems use machine learning for better accuracy.
    """
    score = 0

    # --------------------------------------------------------
    # Check 1: Category Match (40 points max)
    # If categories match exactly, it's a strong signal
    # --------------------------------------------------------
    if lost_item.category == found_item.category:
        score += 40  # Full points for exact category match
    elif are_related_categories(lost_item.category, found_item.category):
        score += 20  # Partial points for related categories

    # --------------------------------------------------------
    # Check 2: Location Similarity (30 points max)
    # Compare the location strings to find common words
    # --------------------------------------------------------
    location_score = calculate_text_similarity(
        lost_item.location.lower(),
        found_item.location.lower()
    )
    score += int(location_score * 30)  # Scale to 30 points

    # --------------------------------------------------------
    # Check 3: Description Keywords (20 points max)
    # Extract keywords and find common ones
    # --------------------------------------------------------
    lost_keywords = extract_keywords(lost_item.title + ' ' + lost_item.description)
    found_keywords = extract_keywords(found_item.title + ' ' + found_item.description)

    # Find common keywords
    common_keywords = lost_keywords.intersection(found_keywords)
    if lost_keywords or found_keywords:
        # Jaccard similarity: intersection / union
        union = lost_keywords.union(found_keywords)
        keyword_similarity = len(common_keywords) / len(union) if union else 0
        score += int(keyword_similarity * 20)

    # --------------------------------------------------------
    # Check 4: Date Proximity (10 points max)
    # Found item should be reported after (or same day as) lost item
    # --------------------------------------------------------
    if lost_item.date_reported and found_item.date_reported:
        days_diff = abs((found_item.date_reported - lost_item.date_reported).days)
        if days_diff == 0:
            score += 10   # Same day
        elif days_diff <= 3:
            score += 7    # Within 3 days
        elif days_diff <= 7:
            score += 5    # Within a week
        elif days_diff <= 30:
            score += 2    # Within a month

    return min(score, 100)  # Cap at 100


def extract_keywords(text):
    """
    Extract meaningful keywords from text.
    Removes common stop words to focus on important terms.
    
    Student Note: Stop words are common words like 'the', 'a', 'is' 
    that don't add meaning to search results.
    """
    # Common stop words to remove
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
        'for', 'of', 'with', 'by', 'from', 'is', 'it', 'was', 'be',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'my', 'i', 'me', 'we', 'you', 'he', 'she', 'they', 'this', 'that',
        'near', 'around', 'area', 'place', 'item', 'lost', 'found'
    }

    # Convert to lowercase and split by non-word characters
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    # Remove stop words and short words
    keywords = {word for word in words if word not in stop_words and len(word) > 2}

    return keywords


def calculate_text_similarity(text1, text2):
    """
    Calculate similarity between two text strings.
    Returns a value between 0 (no similarity) and 1 (identical).
    """
    words1 = set(text1.split())
    words2 = set(text2.split())

    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0

    # Jaccard similarity coefficient
    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union)


def are_related_categories(cat1, cat2):
    """
    Check if two categories are related (e.g., electronics and documents).
    Returns True if categories are related.
    """
    # Define groups of related categories
    related_groups = [
        {'electronics', 'other'},  # Electronics might be 'other' if not sure
        {'documents', 'other'},    # Documents might be listed as other
        {'vehicles', 'keys'},      # Vehicle keys relate to vehicles
        {'clothing', 'jewelry'},   # Accessories and jewelry are related
    ]

    for group in related_groups:
        if cat1 in group and cat2 in group:
            return True

    return False


def find_matches_for_item(item, min_score=40):
    """
    Find potential matches for a given item.
    
    - If item is LOST: look in FOUND items
    - If item is FOUND: look in LOST items
    
    Returns a list of (matched_item, score) tuples sorted by score.
    
    Student Note: This is the main function called from views.py
    when a new item is posted or when viewing an item's detail page.
    """
    matches = []

    if item.item_type == 'lost':
        # Look for found items to match this lost item
        candidates = Item.objects.filter(
            item_type='found',
            is_active=True,
            is_approved=True
        ).exclude(pk=item.pk)

        for candidate in candidates:
            score = calculate_match_score(item, candidate)
            if score >= min_score:
                matches.append({
                    'item': candidate,
                    'score': score,
                    'label': 'Possible Match Found!'
                })

    elif item.item_type == 'found':
        # Look for lost items to match this found item
        candidates = Item.objects.filter(
            item_type='lost',
            is_active=True,
            is_approved=True
        ).exclude(pk=item.pk)

        for candidate in candidates:
            score = calculate_match_score(candidate, item)
            if score >= min_score:
                matches.append({
                    'item': candidate,
                    'score': score,
                    'label': 'Possible Match Found!'
                })

    # Sort by score (highest first)
    matches.sort(key=lambda x: x['score'], reverse=True)

    return matches[:5]  # Return top 5 matches only


def get_match_level(score):
    """
    Convert a numeric score to a human-readable match level.
    
    Student Note: This helps users understand how strong a match is.
    """
    if score >= 80:
        return {'level': 'Strong Match', 'color': 'success', 'icon': '🎯'}
    elif score >= 60:
        return {'level': 'Good Match', 'color': 'info', 'icon': '✅'}
    elif score >= 40:
        return {'level': 'Possible Match', 'color': 'warning', 'icon': '⚠️'}
    else:
        return {'level': 'Weak Match', 'color': 'secondary', 'icon': '❓'}
