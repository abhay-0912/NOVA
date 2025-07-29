"""
Main NOVA Assistant - Clean and Professional Implementation

The core AI assistant that handles user queries, manages conversations,
and coordinates AI responses with a clean, simple architecture.
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime

from .config import NovaConfig
from .logger import get_logger
from ..ai.client import AIClient, AIResponse, AIProvider


class NovaAssistant:
    """
    Main NOVA AI Assistant.
    
    Handles user interactions, manages AI responses, and maintains
    conversation context with a clean, professional interface.
    """
    
    def __init__(self, config: NovaConfig):
        self.config = config
        self.logger = get_logger("assistant")
        self.ai_client: Optional[AIClient] = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the assistant and its components."""
        if self.is_initialized:
            return
        
        self.logger.info(f"Initializing {self.config.name} v{self.config.version}")
        
        # Initialize AI client
        self.ai_client = AIClient(self.config)
        await self.ai_client._ensure_session()
        
        # Log configuration status
        self._log_configuration_status()
        
        self.is_initialized = True
        self.logger.info("NOVA Assistant initialized successfully")
    
    async def shutdown(self):
        """Shutdown the assistant and cleanup resources."""
        if not self.is_initialized:
            return
            
        self.logger.info("Shutting down NOVA Assistant")
        
        if self.ai_client:
            await self.ai_client.close()
        
        self.is_initialized = False
        self.logger.info("NOVA Assistant shutdown complete")
    
    async def process_query(
        self,
        query: str,
        context: Optional[str] = None,
        include_history: bool = True
    ) -> AIResponse:
        """
        Process a user query and return an AI response.
        
        Args:
            query: The user's question or prompt
            context: Optional additional context
            include_history: Whether to include conversation history
            
        Returns:
            AIResponse with the assistant's reply
        """
        if not self.is_initialized:
            await self.initialize()
        
        self.logger.info(f"Processing query: {query[:50]}...")
        
        # Build context from conversation history
        if include_history and self.conversation_history:
            history_context = self._build_history_context()
            if context:
                context = f"{history_context}\n\n{context}"
            else:
                context = history_context
        
        # Generate AI response
        try:
            response = await self.ai_client.generate_response(
                prompt=query,
                context=context,
                system_prompt=self._get_system_prompt()
            )
            
            # Add to conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": response.content,
                "provider": response.provider,
                "model": response.model
            })
            
            # Keep history manageable
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            self.logger.info(f"Response generated using {response.provider} ({response.model})")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Query processing failed: {e}")
            
            # Return error response
            return AIResponse(
                content=f"I apologize, but I encountered an error processing your request: {str(e)}",
                provider="error",
                model="fallback",
                error=str(e)
            )
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        self.logger.info("Conversation history cleared")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation."""
        if not self.conversation_history:
            return {"message": "No conversation history"}
        
        return {
            "total_exchanges": len(self.conversation_history),
            "first_message": self.conversation_history[0]["timestamp"],
            "last_message": self.conversation_history[-1]["timestamp"],
            "providers_used": list(set(
                entry["provider"] for entry in self.conversation_history
            ))
        }
    
    def _log_configuration_status(self):
        """Log the current configuration status."""
        api_keys = []
        if self.config.gemini_api_key:
            api_keys.append("Gemini")
        if self.config.openai_api_key:
            api_keys.append("OpenAI")
        if self.config.anthropic_api_key:
            api_keys.append("Anthropic")
        
        if api_keys:
            self.logger.info(f"🔑 Available AI providers: {', '.join(api_keys)}")
        else:
            self.logger.warning("⚠️ No AI API keys configured - using local responses only")
        
        self.logger.info(f"🎯 Default AI model: {self.config.default_ai_model}")
        
        if self.config.debug:
            self.logger.debug("🐛 Debug mode enabled")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI models."""
        return f"""You are {self.config.name}, a helpful and professional AI assistant.

Guidelines:
- Provide accurate, helpful, and concise responses
- Be professional but friendly in tone
- If you're unsure about something, say so honestly
- Focus on being genuinely helpful to the user
- Keep responses clear and well-structured

Current context: You are running in {self.config.environment} mode."""
    
    def _build_history_context(self) -> str:
        """Build context string from recent conversation history."""
        if not self.conversation_history:
            return ""
        
        # Use last 3 exchanges for context
        recent_history = self.conversation_history[-3:]
        context_parts = []
        
        for entry in recent_history:
            context_parts.append(f"User: {entry['query']}")
            context_parts.append(f"Assistant: {entry['response']}")
        
        return "Recent conversation:\n" + "\n".join(context_parts)


class QueryProcessor:
    """Helper class for processing different types of queries."""
    
    @staticmethod
    def classify_query(query: str) -> str:
        """Classify the type of query to optimize processing."""
        query_lower = query.lower()
        
        if any(op in query_lower for op in ['+', '-', '*', '/', 'calculate', 'math']):
            return "mathematical"
        elif any(word in query_lower for word in ['what is', 'who is', 'when was', 'where is']):
            return "factual"
        elif any(word in query_lower for word in ['how does', 'why does', 'explain', 'describe']):
            return "explanatory"
        elif any(word in query_lower for word in ['create', 'write', 'generate', 'design']):
            return "creative"
        elif any(word in query_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return "greeting"
        else:
            return "general"
    
    @staticmethod
    def extract_intent(query: str) -> Dict[str, Any]:
        """Extract intent and entities from query."""
        return {
            "type": QueryProcessor.classify_query(query),
            "length": len(query.split()),
            "has_question": "?" in query,
            "urgency": "urgent" if any(word in query.lower() for word in ["urgent", "asap", "immediately"]) else "normal"
        }
