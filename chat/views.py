from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .agents import SpiritAssistant
import logging

logger = logging.getLogger(__name__)

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assistant = SpiritAssistant()

    def post(self, request):
        try:
            message = request.data.get('message')
            if not message:
                return Response(
                    {'error': 'Message is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get user context
            user_context = {
                'id': str(request.user.id),
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email
            }
            
            thread_id = f"user_{user_context['id']}"
            logger.debug(f"Processing message: {message} for user: {user_context['name']}")
            
            result = self.assistant.chat(message, user_context, thread_id)
            logger.debug(f"Chat response: {result}")
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )