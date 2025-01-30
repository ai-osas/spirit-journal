# journal/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from .models import JournalEntry, EntryMedia
from .serializers import JournalEntrySerializer
from .utils import neo4j_driver

from unstructured.partition.auto import partition
import logging

logger = logging.getLogger(__name__)

class JournalEntryViewSet(viewsets.ModelViewSet):
    serializer_class = JournalEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            # 1. Create entry in Django
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            entry = serializer.save(user=request.user)

            # 2. Process any media files using unstructured
            media_files = request.FILES.getlist('media')
            media_content = []
            
            for media_file in media_files:
                # Process with unstructured.io
                elements = partition(media_file)
                media_content.extend([str(el) for el in elements])
                
                # Store media file and create EntryMedia object
                # You'll need to implement file storage (S3, etc)
                media_url = "temporary_url"  # Replace with actual storage
                EntryMedia.objects.create(
                    entry=entry,
                    file_type=media_file.content_type.split('/')[0],
                    file_url=media_url
                )

            # 3. Store in Neo4j
            with neo4j_driver.get_session() as session:
                session.run("""
                    CREATE (e:JournalEntry {
                        id: $entry_id,
                        user_id: $user_id,
                        content: $content,
                        created_at: datetime()
                    })
                """, {
                    'entry_id': str(entry.id),
                    'user_id': str(request.user.id),
                    'content': entry.content + '\n' + '\n'.join(media_content)
                })

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating journal entry: {str(e)}")
            return Response(
                {'error': 'Failed to create journal entry'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Get patterns from Neo4j
        with neo4j_driver.get_session() as session:
            patterns = session.run("""
                MATCH (e:JournalEntry {id: $entry_id})
                -[:HAS_PATTERN]->(p:Pattern)
                RETURN p
            """, {'entry_id': str(instance.id)}).data()

        data = serializer.data
        data['patterns'] = patterns
        
        return Response(data)

    @action(detail=True, methods=['post'])
    def analyze_patterns(self, request, pk=None):
        """Endpoint to trigger pattern analysis for an entry"""
        entry = self.get_object()
        
        try:
            # This would call your pattern analysis service
            # We'll implement this in the patterns app
            return Response({'status': 'Pattern analysis initiated'})
        except Exception as e:
            logger.error(f"Error analyzing patterns: {str(e)}")
            return Response(
                {'error': 'Pattern analysis failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )