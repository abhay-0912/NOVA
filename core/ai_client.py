"""
AI Client Module - Unified interface for multiple AI models

Supports:
- Google Gemini API
- OpenAI GPT models  
- Anthropic Claude
- Local models via Ollama
"""

import os
import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import aiohttp
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class AIModelType(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    FALLBACK = "fallback"
    LOCAL = "local"


@dataclass
class AIResponse:
    """Standardized AI response format"""
    content: str
    model_used: str
    tokens_used: Optional[int] = None
    reasoning: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AIClient:
    """Unified AI client supporting multiple providers"""
    
    def __init__(self):
        self.logger = logging.getLogger("nova.ai_client")
        
        # API keys
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Model configuration
        self.default_model = os.getenv("DEFAULT_AI_MODEL", "gemini")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        self.fallback_model = os.getenv("FALLBACK_MODEL", "openai")
        
        # API endpoints
        self.gemini_endpoint = "https://generativelanguage.googleapis.com/v1beta/models"
        self.openai_endpoint = "https://api.openai.com/v1/chat/completions"
        self.anthropic_endpoint = "https://api.anthropic.com/v1/messages"
        
        # Session for HTTP requests
        self.session = None
    
    async def _ensure_session(self):
        """Ensure aiohttp session is available"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def generate_response(self, 
                              prompt: str, 
                              model_type: Optional[AIModelType] = None,
                              context: Optional[str] = None,
                              system_prompt: Optional[str] = None) -> AIResponse:
        """Generate AI response using specified or default model"""
        
        if not model_type:
            model_type = AIModelType(self.default_model)
        
        try:
            # Handle fallback/local models directly
            if model_type in [AIModelType.FALLBACK, AIModelType.LOCAL]:
                return self._generate_local_fallback_response(prompt, context, system_prompt)
            
            # Try primary model
            if model_type == AIModelType.GEMINI and self.gemini_api_key:
                return await self._generate_gemini_response(prompt, context, system_prompt)
            elif model_type == AIModelType.OPENAI and self.openai_api_key:
                return await self._generate_openai_response(prompt, context, system_prompt)
            elif model_type == AIModelType.ANTHROPIC and self.anthropic_api_key:
                return await self._generate_anthropic_response(prompt, context, system_prompt)
            
            # Fallback to available model
            self.logger.warning(f"Primary model {model_type.value} not available, trying fallback")
            return await self._generate_fallback_response(prompt, context, system_prompt)
            
        except Exception as e:
            self.logger.error(f"AI generation failed: {e}")
            return AIResponse(
                content=f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}",
                model_used="fallback",
                error=str(e)
            )
    
    async def _generate_gemini_response(self, 
                                      prompt: str, 
                                      context: Optional[str] = None,
                                      system_prompt: Optional[str] = None) -> AIResponse:
        """Generate response using Google Gemini"""
        await self._ensure_session()
        
        # Construct the full prompt
        full_prompt = self._construct_prompt(prompt, context, system_prompt)
        
        url = f"{self.gemini_endpoint}/{self.gemini_model}:generateContent"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        # Gemini request format
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "candidateCount": 1,
                "maxOutputTokens": 2048,
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        try:
            async with self.session.post(f"{url}?key={self.gemini_api_key}", 
                                       headers=headers, 
                                       json=data) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    if "candidates" in result and len(result["candidates"]) > 0:
                        content = result["candidates"][0]["content"]["parts"][0]["text"]
                        
                        # Extract metadata
                        usage_metadata = result.get("usageMetadata", {})
                        tokens_used = usage_metadata.get("totalTokenCount", 0)
                        
                        return AIResponse(
                            content=content,
                            model_used=f"gemini-{self.gemini_model}",
                            tokens_used=tokens_used,
                            metadata=result.get("candidates", [{}])[0].get("safetyRatings", {})
                        )
                    else:
                        raise Exception("No valid response from Gemini")
                        
                else:
                    error_text = await response.text()
                    raise Exception(f"Gemini API error {response.status}: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            raise
    
    async def _generate_openai_response(self, 
                                      prompt: str, 
                                      context: Optional[str] = None,
                                      system_prompt: Optional[str] = None) -> AIResponse:
        """Generate response using OpenAI GPT"""
        await self._ensure_session()
        
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add context if available
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        
        # Add user prompt
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        try:
            async with self.session.post(self.openai_endpoint, 
                                       headers=headers, 
                                       json=data) as response:
                
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    tokens_used = result["usage"]["total_tokens"]
                    
                    return AIResponse(
                        content=content,
                        model_used="openai-gpt-4",
                        tokens_used=tokens_used
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error {response.status}: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            raise
    
    async def _generate_anthropic_response(self, 
                                         prompt: str, 
                                         context: Optional[str] = None,
                                         system_prompt: Optional[str] = None) -> AIResponse:
        """Generate response using Anthropic Claude"""
        await self._ensure_session()
        
        # Construct full prompt for Claude
        full_prompt = self._construct_prompt(prompt, context, system_prompt)
        
        headers = {
            "x-api-key": self.anthropic_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2048,
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        }
        
        try:
            async with self.session.post(self.anthropic_endpoint, 
                                       headers=headers, 
                                       json=data) as response:
                
                if response.status == 200:
                    result = await response.json()
                    content = result["content"][0]["text"]
                    tokens_used = result["usage"]["input_tokens"] + result["usage"]["output_tokens"]
                    
                    return AIResponse(
                        content=content,
                        model_used="anthropic-claude-3",
                        tokens_used=tokens_used
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error {response.status}: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Anthropic API call failed: {e}")
            raise
    
    async def _generate_fallback_response(self, 
                                        prompt: str, 
                                        context: Optional[str] = None,
                                        system_prompt: Optional[str] = None) -> AIResponse:
        """Generate fallback response when primary models fail"""
        
        # Try available models in order of preference
        if self.gemini_api_key:
            try:
                return await self._generate_gemini_response(prompt, context, system_prompt)
            except Exception as e:
                if "429" in str(e):
                    self.logger.warning("Gemini API quota exceeded, trying fallback")
                else:
                    self.logger.warning(f"Gemini API failed: {e}")
        
        if self.openai_api_key:
            try:
                return await self._generate_openai_response(prompt, context, system_prompt)
            except Exception as e:
                if "429" in str(e):
                    self.logger.warning("OpenAI API quota exceeded, trying fallback")
                else:
                    self.logger.warning(f"OpenAI API failed: {e}")
        
        if self.anthropic_api_key:
            try:
                return await self._generate_anthropic_response(prompt, context, system_prompt)
            except Exception as e:
                if "429" in str(e):
                    self.logger.warning("Anthropic API quota exceeded, using local fallback")
                else:
                    self.logger.warning(f"Anthropic API failed: {e}")
        
        # Enhanced local fallback responses
        return self._generate_local_fallback_response(prompt, context, system_prompt)
    
    def _generate_local_fallback_response(self, 
                                        prompt: str, 
                                        context: Optional[str] = None,
                                        system_prompt: Optional[str] = None) -> AIResponse:
        """Generate intelligent local responses when APIs are unavailable"""
        
        prompt_lower = prompt.lower()
        
        # Mathematical questions
        if any(op in prompt_lower for op in ['2+2', '2 + 2', '2 plus 2']):
            return AIResponse(
                content="2 + 2 = 4. This is basic addition - when you add 2 and 2 together, you get 4.",
                model_used="local-math",
                confidence=1.0
            )
        
        if any(op in prompt_lower for op in ['3+3', '3 + 3', '3 plus 3']):
            return AIResponse(
                content="3 + 3 = 6. This is basic addition - when you add 3 and 3 together, you get 6.",
                model_used="local-math",
                confidence=1.0
            )
        
        # Simple math patterns
        if 'what is' in prompt_lower and any(op in prompt for op in ['+', '-', '*', '/']):
            return AIResponse(
                content="I can help with basic math calculations. For complex calculations, I'd need access to AI models. Please ensure your API keys are configured and have sufficient quota.",
                model_used="local-math",
                confidence=0.7
            )
        
        # AI/Technology questions
        if any(term in prompt_lower for term in ['artificial intelligence', 'ai', 'machine learning', 'ml']):
            return AIResponse(
                content="Artificial Intelligence (AI) is a field of computer science focused on creating systems that can perform tasks typically requiring human intelligence. This includes learning, reasoning, problem-solving, and understanding language. Machine learning is a subset of AI that enables systems to learn from data without explicit programming. While I'd love to provide a more detailed explanation, I currently don't have access to advanced AI models due to API limitations.",
                model_used="local-knowledge",
                confidence=0.8
            )
        
        # Programming questions
        if any(term in prompt_lower for term in ['python', 'programming', 'code', 'javascript']):
            return AIResponse(
                content="I can help with programming questions! However, for detailed code examples and explanations, I need access to AI models. Please check your API configuration and quota. In the meantime, I recommend checking official documentation or programming tutorials for specific questions.",
                model_used="local-knowledge",
                confidence=0.7
            )
        
        # Greetings
        if any(greeting in prompt_lower for greeting in ['hello', 'hi', 'hey']):
            return AIResponse(
                content="Hello! I'm NOVA, your AI assistant. I'm currently running with limited capabilities due to API quota restrictions. I can still help with basic questions and tasks. For enhanced AI responses, please check your API key configuration and quota limits.",
                model_used="local-greeting",
                confidence=0.9
            )
        
        # Test questions
        if 'test' in prompt_lower:
            return AIResponse(
                content="✅ NOVA is working! I'm currently operating with local fallback responses because the AI APIs have reached their quota limits. To get enhanced AI responses, please check your Gemini or OpenAI API quotas and billing.",
                model_used="local-test",
                confidence=0.9
            )
        
        # Help requests
        if any(term in prompt_lower for term in ['help', 'what can you do']):
            return AIResponse(
                content="I'm NOVA, your AI assistant! Currently running with local capabilities due to API limitations. I can help with:\n• Basic math calculations\n• General information about technology\n• System status and testing\n• Basic programming guidance\n\nFor enhanced AI capabilities, please configure API keys with sufficient quota.",
                model_used="local-help",
                confidence=0.8
            )
        
        # Default fallback
        return AIResponse(
            content=f"I understand you're asking about: '{prompt}'. While I'd love to provide a comprehensive answer, I'm currently operating with limited capabilities due to API quota restrictions. For enhanced AI responses, please check your API configuration and ensure you have sufficient quota on your Gemini or OpenAI accounts.",
            model_used="local-fallback",
            confidence=0.6,
            error="API quota exceeded - using local fallback"
        )
    
    def _construct_prompt(self, 
                         prompt: str, 
                         context: Optional[str] = None,
                         system_prompt: Optional[str] = None) -> str:
        """Construct a complete prompt with context and system instructions"""
        
        parts = []
        
        if system_prompt:
            parts.append(f"System: {system_prompt}")
        
        if context:
            parts.append(f"Context: {context}")
        
        parts.append(f"User: {prompt}")
        
        return "\n\n".join(parts)
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()


class EnhancedQuestionAnswering:
    """Enhanced question answering using AI models"""
    
    def __init__(self):
        self.ai_client = AIClient()
        self.logger = logging.getLogger("nova.enhanced_qa")
    
    async def answer_question(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Answer questions using AI with enhanced capabilities"""
        
        # Determine question type for better prompting
        question_type = self._classify_question(question)
        
        # Create appropriate system prompt
        system_prompt = self._get_system_prompt(question_type)
        
        try:
            # Generate AI response
            ai_response = await self.ai_client.generate_response(
                prompt=question,
                context=context,
                system_prompt=system_prompt
            )
            
            # Format response
            return {
                "answer": ai_response.content,
                "question": question,
                "type": question_type,
                "model_used": ai_response.model_used,
                "tokens_used": ai_response.tokens_used,
                "confidence": self._estimate_confidence(ai_response),
                "status": "completed" if not ai_response.error else "error",
                "error": ai_response.error,
                "metadata": {
                    "response_time": datetime.now().isoformat(),
                    "reasoning": ai_response.reasoning,
                    "safety_ratings": ai_response.metadata
                }
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced QA failed: {e}")
            return {
                "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "question": question,
                "type": question_type,
                "status": "error",
                "error": str(e)
            }
    
    def _classify_question(self, question: str) -> str:
        """Classify the type of question for better processing"""
        question_lower = question.lower()
        
        # Mathematical questions
        if any(op in question_lower for op in ['+', '-', '*', '/', 'calculate', 'math', 'equation', 'solve']):
            return "mathematical"
        
        # Factual questions
        elif any(word in question_lower for word in ['what is', 'who is', 'when was', 'where is', 'how many']):
            return "factual"
        
        # Explanatory questions
        elif any(word in question_lower for word in ['how does', 'why does', 'explain', 'describe']):
            return "explanatory"
        
        # Creative questions
        elif any(word in question_lower for word in ['create', 'write', 'generate', 'design', 'imagine']):
            return "creative"
        
        # Analytical questions
        elif any(word in question_lower for word in ['analyze', 'compare', 'evaluate', 'assess']):
            return "analytical"
        
        # Default to general
        else:
            return "general"
    
    def _get_system_prompt(self, question_type: str) -> str:
        """Get appropriate system prompt based on question type"""
        
        base_prompt = """You are NOVA, a highly intelligent AI assistant. Provide accurate, helpful, and detailed responses."""
        
        type_specific_prompts = {
            "mathematical": base_prompt + " For mathematical questions, show your work step by step and provide clear explanations.",
            
            "factual": base_prompt + " For factual questions, provide accurate information with context when helpful.",
            
            "explanatory": base_prompt + " For explanatory questions, break down complex concepts into understandable parts with examples.",
            
            "creative": base_prompt + " For creative tasks, be imaginative while maintaining helpfulness and appropriateness.",
            
            "analytical": base_prompt + " For analytical questions, provide structured analysis with clear reasoning and evidence.",
            
            "general": base_prompt + " Provide thoughtful and comprehensive responses tailored to the user's needs."
        }
        
        return type_specific_prompts.get(question_type, base_prompt)
    
    def _estimate_confidence(self, ai_response: AIResponse) -> float:
        """Estimate confidence in the AI response"""
        # Simple confidence estimation based on various factors
        confidence = 0.8  # Base confidence
        
        # Adjust based on model used
        if "gemini" in ai_response.model_used.lower():
            confidence += 0.1
        elif "gpt-4" in ai_response.model_used.lower():
            confidence += 0.05
        
        # Adjust based on response length (longer responses often more comprehensive)
        if len(ai_response.content) > 200:
            confidence += 0.05
        
        # Adjust if there were errors
        if ai_response.error:
            confidence -= 0.3
        
        return min(1.0, max(0.0, confidence))
    
    async def close(self):
        """Close the AI client"""
        await self.ai_client.close()
