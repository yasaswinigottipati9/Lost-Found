"""
Initial Migration for Lost & Found Smart Platform
==================================================
Student Note: Migrations are auto-generated files that Django uses
to create and modify database tables. 
Run: python manage.py migrate
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create UserProfile table
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('address', models.TextField(blank=True)),
                ('profile_photo', models.ImageField(blank=True, null=True, upload_to='profile_photos/')),
                ('bio', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'User Profile', 'verbose_name_plural': 'User Profiles'},
        ),
        # Create Item table
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('category', models.CharField(choices=[('electronics', 'Electronics'), ('documents', 'Documents'), ('vehicles', 'Vehicles'), ('clothing', 'Clothing & Accessories'), ('keys', 'Keys'), ('jewelry', 'Jewelry'), ('animals', 'Animals/Pets'), ('books', 'Books & Stationery'), ('sports', 'Sports Equipment'), ('other', 'Other')], default='other', max_length=50)),
                ('description', models.TextField()),
                ('item_type', models.CharField(choices=[('lost', 'Lost'), ('found', 'Found')], max_length=10)),
                ('location', models.CharField(max_length=300)),
                ('location_detail', models.TextField(blank=True)),
                ('date_reported', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='items/')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('matched', 'Matched'), ('pending_verification', 'Pending Verification'), ('delivered', 'Delivered')], default='pending', max_length=30)),
                ('contact_phone', models.CharField(blank=True, max_length=15)),
                ('contact_email', models.EmailField(blank=True)),
                ('is_approved', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at'], 'verbose_name': 'Item', 'verbose_name_plural': 'Items'},
        ),
        # Create MatchRequest table
        migrations.CreateModel(
            name='MatchRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('match_score', models.FloatField(default=0.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True)),
                ('found_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='found_matches', to='lostfound.item')),
                ('lost_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lost_matches', to='lostfound.item')),
            ],
            options={'verbose_name': 'Match Request', 'verbose_name_plural': 'Match Requests', 'unique_together': {('lost_item', 'found_item')}},
        ),
        # Create ChatMessage table
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='lostfound.item')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['timestamp'], 'verbose_name': 'Chat Message', 'verbose_name_plural': 'Chat Messages'},
        ),
        # Create ItemVerification table
        migrations.CreateModel(
            name='ItemVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verification_detail', models.TextField()),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='verification', to='lostfound.item')),
                ('verified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verifications_done', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Item Verification', 'verbose_name_plural': 'Item Verifications'},
        ),
    ]
