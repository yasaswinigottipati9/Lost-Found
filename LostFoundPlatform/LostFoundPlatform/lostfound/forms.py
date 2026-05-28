"""
Forms for Lost & Found Smart Platform
======================================
Student Note: Django forms handle user input validation and rendering.
ModelForm automatically creates form fields from a model's fields.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Item, UserProfile, ChatMessage, ItemVerification


# ============================================================
# FORM 1: User Registration Form
# ============================================================
class UserRegistrationForm(UserCreationForm):
    """
    Extended registration form with extra fields.
    Student Note: UserCreationForm is a built-in Django form for user registration.
    We extend it to add email, first_name, last_name fields.
    """
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=15, required=False, help_text='Optional phone number')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        """Override save to also save extra fields"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Create UserProfile for this new user
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data.get('phone', '')
            )
        return user


# ============================================================
# FORM 2: Post Item Form (for both Lost and Found items)
# ============================================================
class ItemForm(forms.ModelForm):
    """
    Form for posting a lost or found item.
    Student Note: ModelForm reads the model fields and creates form fields automatically.
    We can customize widgets (HTML form elements) for each field.
    """
    class Meta:
        model = Item
        fields = [
            'title', 'category', 'description', 'item_type',
            'location', 'location_detail', 'date_reported',
            'image', 'contact_phone', 'contact_email'
        ]
        widgets = {
            # Bootstrap-styled inputs using 'attrs' to add CSS classes
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., iPhone 13, Blue Bicycle, PAN Card'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the item in detail (color, brand, size, unique features...)'
            }),
            'item_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., MG Road, Bengaluru'
            }),
            'location_detail': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'More specific location details...'
            }),
            'date_reported': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'    # HTML5 date picker
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 98765 43210'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
        }

    def clean_image(self):
        """Validate image file size (max 5MB)"""
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file size must be under 5MB.")
        return image


# ============================================================
# FORM 3: Search and Filter Form
# ============================================================
class SearchFilterForm(forms.Form):
    """
    Form for searching and filtering items on the dashboard.
    Student Note: This is a plain Form (not ModelForm) since it
    doesn't directly relate to a database model.
    """
    from .models import CATEGORY_CHOICES, ITEM_TYPE_CHOICES

    keyword = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by keyword...'
        })
    )
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    item_type = forms.ChoiceField(
        choices=[('', 'Lost & Found'), ('lost', 'Lost'), ('found', 'Found')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by location...'
        })
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


# ============================================================
# FORM 4: Chat Message Form
# ============================================================
class ChatMessageForm(forms.ModelForm):
    """Form for sending chat messages"""
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message here...',
                'id': 'messageInput'
            })
        }


# ============================================================
# FORM 5: Item Verification Form
# ============================================================
class ItemVerificationForm(forms.ModelForm):
    """Form for verifying ownership before delivering item"""
    class Meta:
        model = ItemVerification
        fields = ['verification_detail', 'notes']
        widgets = {
            'verification_detail': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter proof of ownership (IMEI number, document number, serial number, etc.)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes...'
            }),
        }


# ============================================================
# FORM 6: User Profile Edit Form
# ============================================================
class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'bio', 'profile_photo']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
