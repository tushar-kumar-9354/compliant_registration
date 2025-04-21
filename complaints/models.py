from django.contrib.auth.models import AbstractUser
from django.db import models
from utils.genai import is_duplicate_complaint, tone_to_emoji, is_toxic

class User(AbstractUser):
    ROLE_CHOICES = (
        ('citizen', 'Citizen'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='citizen')

    def __str__(self):
        return self.username

class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ('pothole', 'Pothole'),
        ('garbage', 'Garbage'),
        ('light', 'Streetlight'),
        ('water', 'Water Leakage'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    image = models.ImageField(upload_to='complaints/images/', blank=True, null=True)
    voice_note = models.FileField(upload_to='complaints/voice/', blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField(blank=True)
    assigned_to = models.ForeignKey('Officer', on_delete=models.SET_NULL, null=True, blank=True)
    is_seen = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    # AI/NLP features
    summary = models.TextField(blank=True, null=True)
    suggested_category = models.CharField(max_length=255, blank=True, null=True)
    tone = models.CharField(max_length=20, blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    auto_response = models.TextField(blank=True, null=True)
    is_duplicate = models.BooleanField(default=False)
    duplicate_score = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.description:
            existing = Complaint.objects.exclude(id=self.id).values_list('description', flat=True)
            is_dup, score = is_duplicate_complaint(self.description, list(existing))
            self.is_duplicate = is_dup
            self.duplicate_score = score if is_dup else None
        super().save(*args, **kwargs)

    @property
    def tone_emoji(self):
        return tone_to_emoji(self.tone or "")

    @property
    def is_toxic_content(self):
        return is_toxic(self.description)

    def __str__(self):
        return f"{self.category} | {self.status} | by {self.user.username}"

class StatusUpdate(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='status_updates')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    new_status = models.CharField(max_length=20)
    note = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.complaint.id} - {self.new_status} - {self.timestamp.strftime('%d-%b %H:%M')}"

class Officer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    badge_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.badge_number})"
