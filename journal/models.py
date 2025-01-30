# journal/models.py
from django.db import models
from django.contrib.auth import get_user_model
from uuid import uuid4

User = get_user_model()

class JournalEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class EntryMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    entry = models.ForeignKey(JournalEntry, related_name='media', on_delete=models.CASCADE)
    file_type = models.CharField(max_length=20)  # 'image', 'audio'
    file_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)