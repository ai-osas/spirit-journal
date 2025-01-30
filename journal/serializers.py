# journal/serializers.py
from rest_framework import serializers
from .models import JournalEntry, EntryMedia

class EntryMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryMedia
        fields = ['id', 'file_type', 'file_url', 'created_at']

class JournalEntrySerializer(serializers.ModelSerializer):
    media = EntryMediaSerializer(many=True, read_only=True)
    
    class Meta:
        model = JournalEntry
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'media']
        read_only_fields = ['id', 'created_at', 'updated_at']