# Lost & Found Smart Platform
## Complete Setup Guide & Documentation

---

## 📋 Project Overview

**Lost & Found Smart Platform** is a Django-based web application that helps users:
- Report lost or found items with photos
- Automatically match lost items with found items
- Chat securely to verify and return items
- Track item status from Lost → Matched → Verified → Delivered

**Technology Stack:**
- **Backend:** Python 3.11 + Django 4.2
- **Database:** MySQL 8.0
- **Frontend:** HTML5 + Bootstrap 5 + JavaScript
- **File Storage:** Django media files (local)

---

## 📁 Project Folder Structure

```
LostFoundPlatform/
├── manage.py                          # Django management utility
├── requirements.txt                   # Python dependencies
├── README.md                          # This file
│
├── lostandfound_project/              # Main project settings folder
│   ├── __init__.py
│   ├── settings.py                    # All configuration (DB, apps, etc.)
│   ├── urls.py                        # Root URL routing
│   └── wsgi.py                        # Web server interface
│
├── lostfound/                         # Main Django application
│   ├── __init__.py
│   ├── models.py                      # Database models (Item, Chat, Match, etc.)
│   ├── views.py                       # Business logic for each page
│   ├── urls.py                        # App URL routing
│   ├── forms.py                       # Django forms for user input
│   ├── admin.py                       # Admin panel configuration
│   ├── matching.py                    # Item matching algorithm
│   │
│   ├── migrations/                    # Database migration files (auto-generated)
│   │   └── __init__.py
│   │
│   ├── fixtures/                      # Sample data for testing
│   │   └── sample_data.json
│   │
│   ├── static/                        # Static files (CSS, JS, images)
│   │   ├── css/
│   │   │   └── style.css              # Custom styles
│   │   ├── js/
│   │   │   └── main.js                # Custom JavaScript
│   │   └── images/                    # Static images
│   │
│   └── templates/                     # HTML templates
│       ├── lostfound/
│       │   ├── base.html              # Base template (navbar, footer)
│       │   ├── home.html              # Home page
│       │   ├── dashboard.html         # All items dashboard
│       │   ├── item_card.html         # Reusable item card component
│       │   ├── item_detail.html       # Item detail page
│       │   ├── post_item.html         # Post lost/found item
│       │   ├── chat.html              # Chat interface
│       │   ├── user_dashboard.html    # Personal dashboard
│       │   ├── verify_item.html       # Verification page
│       │   ├── profile.html           # User profile
│       │   └── confirm_delete.html    # Delete confirmation
│       └── registration/
│           ├── login.html             # Login page
│           └── register.html          # Registration page
│
└── media/                             # User uploaded files (auto-created)
    └── items/                         # Item images stored here
```

---

## 🗄️ Database Models

### 1. User (Django Built-in)
- id, username, email, first_name, last_name, password, is_staff

### 2. UserProfile
- user (OneToOne → User)
- phone, address, bio, profile_photo, created_at

### 3. Item ⭐ (Main Model)
- id, user (FK → User)
- title, category, description
- item_type: **lost** or **found**
- location, location_detail, date_reported
- image (uploaded file)
- status: **pending** → **matched** → **pending_verification** → **delivered**
- contact_phone, contact_email
- is_approved (admin control), is_active (soft delete)

### 4. MatchRequest
- id, lost_item (FK → Item), found_item (FK → Item)
- match_score (0-100), status, created_at

### 5. ChatMessage
- id, sender (FK → User), receiver (FK → User)
- item (FK → Item, optional)
- message, timestamp, is_read

### 6. ItemVerification
- id, item (OneToOne → Item)
- verification_detail (IMEI, doc number, etc.)
- verified_by, verified_at, is_verified

---

## 🚀 Step-by-Step Setup Instructions

### Step 1: Install Prerequisites

```bash
# Install Python 3.11+
python --version   # Should show 3.8+

# Install pip
pip --version

# Install MySQL Server
# Windows: Download MySQL Installer from mysql.com
# Ubuntu/Mac: sudo apt install mysql-server
```

### Step 2: Create MySQL Database

```sql
-- Open MySQL terminal or MySQL Workbench
-- Run these commands:

CREATE DATABASE lostandfound_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'lostfound_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON lostandfound_db.* TO 'lostfound_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3: Extract Project & Setup Python Environment

```bash
# Navigate to project directory
cd LostFoundPlatform

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Database in settings.py

Open `lostandfound_project/settings.py` and update the DATABASES section:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lostandfound_db',      # Database name you created
        'USER': 'lostfound_user',        # MySQL username
        'PASSWORD': 'your_password',     # MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Step 5: Run Database Migrations

```bash
# This creates all the database tables based on models.py
python manage.py makemigrations
python manage.py migrate

# You should see output like:
# Applying lostfound.0001_initial... OK
```

### Step 6: Create Admin User

```bash
python manage.py createsuperuser

# Enter details when prompted:
# Username: admin
# Email: admin@example.com
# Password: (choose a strong password)
```

### Step 7: Load Sample Data (Optional)

```bash
# Note: Sample data uses hashed passwords, create real users through registration
# First create users via /register/ then load items

# OR load fixture (may need to adjust user PKs)
python manage.py loaddata lostfound/fixtures/sample_data.json
```

### Step 8: Collect Static Files

```bash
python manage.py collectstatic
# Type 'yes' when prompted
```

### Step 9: Run the Development Server

```bash
python manage.py runserver

# Open your browser and go to:
# http://127.0.0.1:8000/          → Home page
# http://127.0.0.1:8000/admin/    → Admin panel
# http://127.0.0.1:8000/register/ → Register a new account
```

---

## 📱 Pages & URLs

| URL | Page | Login Required |
|-----|------|---------------|
| `/` | Home Page | No |
| `/dashboard/` | All Items Dashboard | No |
| `/register/` | User Registration | No |
| `/login/` | Login | No |
| `/post-item/` | Post Lost/Found Item | ✅ Yes |
| `/item/<id>/` | Item Detail | No |
| `/item/<id>/edit/` | Edit Item | ✅ Yes (owner) |
| `/item/<id>/delete/` | Delete Item | ✅ Yes (owner) |
| `/item/<id>/verify/` | Verify & Deliver | ✅ Yes (owner) |
| `/chat/<user_id>/` | Chat with User | ✅ Yes |
| `/my-dashboard/` | Personal Dashboard | ✅ Yes |
| `/profile/` | User Profile | ✅ Yes |
| `/admin/` | Admin Panel | ✅ Admin only |

---

## 🧠 Item Matching Algorithm

The matching system (`lostfound/matching.py`) compares items using a score:

| Factor | Points |
|--------|--------|
| Same category | 40 pts |
| Related categories | 20 pts |
| Similar location | 0-30 pts |
| Common keywords | 0-20 pts |
| Date proximity (same day) | 10 pts |
| Date proximity (within 3 days) | 7 pts |
| Date proximity (within a week) | 5 pts |

**Match Levels:**
- 80+ points → Strong Match 🎯
- 60-79 points → Good Match ✅
- 40-59 points → Possible Match ⚠️

---

## 💬 Chat System

The chat system uses Django's ORM for message storage:
- Messages stored in `ChatMessage` model
- Auto-marks messages as read when opened
- Refreshes every 15 seconds (simple polling)
- Supports attaching messages to specific items

**For Production:** Upgrade to WebSockets using Django Channels for real-time chat.

---

## 🔐 Verification Process

1. Lost item owner and finder connect via chat
2. Finder verifies ownership (IMEI, document number, etc.)
3. Owner goes to item → "Mark as Delivered"
4. Enters verification details
5. Item status changes to **Delivered**
6. Item appears in "Delivered" tab on dashboard

---

## 👨‍💼 Admin Panel Features

Access at `/admin/` with superuser credentials:

- **View all items** → approve, reject, or delete
- **Manage users** → view all registered users
- **Chat messages** → monitor conversations
- **Match requests** → manage item matches
- **Bulk actions** → approve/reject multiple items at once

---

## 🛠️ Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'MySQLdb'` | Run: `pip install mysqlclient` |
| `Access denied for user 'root'@'localhost'` | Check MySQL username/password in settings.py |
| `Can't upload image` | Create `media/items/` directory manually |
| `TemplateDoesNotExist` | Check template paths in settings.py TEMPLATES |
| Static files not loading | Run `python manage.py collectstatic` |
| Port already in use | Use `python manage.py runserver 8080` |

---

## 📚 Student Learning Points

1. **Django MVT Pattern** - Models (DB), Views (Logic), Templates (UI)
2. **ORM Queries** - `filter()`, `Q()`, `annotate()`, `order_by()`
3. **Forms & Validation** - ModelForm, field validation, CSRF protection
4. **File Uploads** - ImageField, MEDIA_ROOT, MEDIA_URL
5. **Authentication** - `@login_required`, `request.user`, sessions
6. **Admin Panel** - `list_display`, `list_filter`, custom actions
7. **URL Routing** - `path()`, `include()`, named URLs, URL parameters
8. **Template Tags** - `{% for %}`, `{% if %}`, `{% url %}`, `{% static %}`
9. **Bootstrap 5** - Cards, badges, tabs, modals, responsive grid
10. **Matching Algorithm** - Text similarity, scoring system

---

## 🎓 Project Submission Checklist

- [ ] All models created and migrated
- [ ] All 10 pages working
- [ ] User registration and login working
- [ ] Image upload working
- [ ] Search and filter working
- [ ] Matching algorithm showing results
- [ ] Chat system working
- [ ] Admin panel configured
- [ ] Sample data loaded
- [ ] README documentation complete

---

*Lost & Found Smart Platform — Academic Project | Django 4.2 | Bootstrap 5*
