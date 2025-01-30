from typing import Annotated, TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from django.conf import settings
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class UserContext(TypedDict):
    id: str
    name: Optional[str]
    email: Optional[str]

class SpiritState(TypedDict):
    messages: Annotated[list, add_messages]
    follow_up_questions: list
    user_context: UserContext

class SpiritAssistant:
    def __init__(self):
        logger.info("Initializing SpiritAssistant")
        self.llm = ChatAnthropic(
            api_key=settings.ANTHROPIC_API_KEY,
            model="claude-3-sonnet-20240229"
        )
        self.memory = MemorySaver()
        self.graph = self._create_graph()
        
    def _create_graph(self):
        logger.info("Creating graph")
        graph = StateGraph(SpiritState)
        
        # Add nodes
        graph.add_node("chat", self._spirit_chat)
        graph.add_node("follow_ups", self._generate_follow_ups)
        
        # Add edges with proper flow
        graph.add_edge(START, "chat")
        graph.add_edge("chat", "follow_ups")
        graph.add_edge("follow_ups", END)
        
        return graph.compile(checkpointer=self.memory)

    def _spirit_chat(self, state: SpiritState):
        """Core chat function with gentle, supportive personality"""
        logger.debug(f"Processing chat with state: {state}")

        user_context = state.get("user_context", {})
        user_name = user_context.get("name", "there")
        
        system_prompt = f"""You are a kind, gentle spirit guide helping {user_name} understand their learning journey.
        Your role is to listen deeply and reflect thoughtfully, helping them discover their own insights.
        
        Core traits:
        - Respond with warmth and genuine empathy
        - Focus on understanding rather than directing
        - Mirror their language and pace
        - Acknowledge and validate their experiences
        - Ask gentle, open-ended questions that encourage reflection
        
        Remember their context: {user_context}
        """
        
        try:
            response = self.llm.invoke([
                ("system", system_prompt),
                *state["messages"]
            ])
            logger.debug(f"LLM Response: {response}")
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"Error in spirit_chat: {str(e)}")
            raise

    def _generate_follow_ups(self, state: SpiritState):
        """Generate first-person follow-up questions for self-reflection"""
        if not state["messages"]:
            return {"follow_up_questions": []}
            
        last_message = state["messages"][-1]
        message_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
                
        prompt = f"""Based on this personal insight: "{message_content}"

        Generate 2-3 follow-up questions that I might ask myself to explore this insight further.
        These should be first-person questions that help me understand my own learning patterns and processes.

        Important guidelines:
        - Questions should start with "Why do I...", "How do I...", "What if I...", "Am I...", etc.
        - Focus on self-discovery and pattern recognition
        - Help me explore the broader implications of my observation
        - Questions should help me understand myself better

        Example style for a coding insight:
        - "Why do I find this way of learning more effective?"
        - "How does this pattern show up in other areas of my learning?"
        - "What does this tell me about my natural learning style?"

        Format: Return only the questions, one per line, nothing else.
        """
        
        try:
            response = self.llm.invoke(prompt)
            logger.debug(f"Follow-up response: {response}")
            
            if hasattr(response, 'content'):
                questions = [q.strip() for q in response.content.split('\n') if q.strip()]
            else:
                questions = [q.strip() for q in str(response).split('\n') if q.strip()]
            
            logger.debug(f"Extracted questions: {questions}")
            return {"follow_up_questions": questions[:3]}
            
        except Exception as e:
            logger.error(f"Error generating follow-ups: {str(e)}")
            return {"follow_up_questions": []}

    def chat(self, message: str, user_context: dict, thread_id: str = "default"):
        """Process a message and return response with follow-ups"""
        logger.info(f"Processing chat message: {message} for thread: {thread_id}")
        
        try:
            config = {"configurable": {"thread_id": thread_id}}
            events = self.graph.stream(
                {
                    "messages": [("user", message)],
                    "user_context": user_context,
                    "follow_up_questions": []
                },
                config
            )
            
            response = None
            follow_ups = []
            
            for event in events:
                for key, value in event.items():
                    if "messages" in value and value["messages"]:
                        response = value["messages"][-1]
                    if "follow_up_questions" in value:
                        follow_ups = value["follow_up_questions"]
            
            return {
                "message": response.content if response else "",
                "followUpQuestions": follow_ups
            }
                
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}", exc_info=True)
            raise