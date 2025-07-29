"""
Professional AI Client for NOVA

Clean, simple implementation supporting multiple AI providers with intelligent
fallbacks and professional error handling.
"""

import asyncio
import aiohttp
import json
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..core.config import NovaConfig
from ..core.logger import get_logger


class AIProvider(Enum):
    """Supported AI providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


@dataclass
class AIResponse:
    """Standardized AI response."""
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Check if response was successful."""
        return self.error is None


class AIClient:
    """Professional AI client with multi-provider support."""
    
    def __init__(self, config: NovaConfig):
        self.config = config
        self.logger = get_logger("ai")
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.ai_timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def generate_response(
        self,
        prompt: str,
        provider: Optional[AIProvider] = None,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        """
        Generate AI response with automatic provider selection and fallbacks.
        
        Args:
            prompt: The user's prompt/question
            provider: Preferred AI provider (auto-selected if None)
            context: Additional context for the prompt
            system_prompt: System-level instructions
            
        Returns:
            AIResponse with generated content
        """
        # Auto-select provider if not specified
        if provider is None:
            provider = self._select_provider()
        
        # Try primary provider
        try:
            if provider == AIProvider.GEMINI and self.config.gemini_api_key:
                return await self._generate_gemini(prompt, context, system_prompt)
            elif provider == AIProvider.OPENAI and self.config.openai_api_key:
                return await self._generate_openai(prompt, context, system_prompt)
            elif provider == AIProvider.ANTHROPIC and self.config.anthropic_api_key:
                return await self._generate_anthropic(prompt, context, system_prompt)
            elif provider == AIProvider.LOCAL:
                return self._generate_local(prompt, context, system_prompt)
        except Exception as e:
            self.logger.warning(f"Primary provider {provider.value} failed: {e}")
        
        # Try fallback providers
        return await self._generate_fallback(prompt, context, system_prompt)
    
    def _select_provider(self) -> AIProvider:
        """Select the best available AI provider."""
        if self.config.default_ai_model == "gemini" and self.config.gemini_api_key:
            return AIProvider.GEMINI
        elif self.config.default_ai_model == "openai" and self.config.openai_api_key:
            return AIProvider.OPENAI
        elif self.config.default_ai_model == "anthropic" and self.config.anthropic_api_key:
            return AIProvider.ANTHROPIC
        else:
            return AIProvider.LOCAL
    
    async def _generate_gemini(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        """Generate response using Google Gemini."""
        await self._ensure_session()
        
        full_prompt = self._build_prompt(prompt, context, system_prompt)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.gemini_model}:generateContent"
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": self.config.ai_temperature,
                "maxOutputTokens": self.config.ai_max_tokens,
                "candidateCount": 1
            }
        }
        
        async with self.session.post(
            f"{url}?key={self.config.gemini_api_key}",
            headers=headers,
            json=data
        ) as response:
            if response.status == 200:
                result = await response.json()
                if "candidates" in result and result["candidates"]:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    tokens = result.get("usageMetadata", {}).get("totalTokenCount", 0)
                    
                    return AIResponse(
                        content=content,
                        provider="gemini",
                        model=self.config.gemini_model,
                        tokens_used=tokens
                    )
            
            error_text = await response.text()
            raise Exception(f"Gemini API error {response.status}: {error_text}")
    
    async def _generate_openai(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        """Generate response using OpenAI."""
        await self._ensure_session()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        messages.append({"role": "user", "content": prompt})
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.openai_model,
            "messages": messages,
            "temperature": self.config.ai_temperature,
            "max_tokens": self.config.ai_max_tokens
        }
        
        async with self.session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                tokens = result["usage"]["total_tokens"]
                
                return AIResponse(
                    content=content,
                    provider="openai",
                    model=self.config.openai_model,
                    tokens_used=tokens
                )
            
            error_text = await response.text()
            raise Exception(f"OpenAI API error {response.status}: {error_text}")
    
    async def _generate_anthropic(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        """Generate response using Anthropic Claude."""
        await self._ensure_session()
        
        full_prompt = self._build_prompt(prompt, context, system_prompt)
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.config.anthropic_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.config.anthropic_model,
            "max_tokens": self.config.ai_max_tokens,
            "messages": [{"role": "user", "content": full_prompt}]
        }
        
        async with self.session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                content = result["content"][0]["text"]
                tokens = result["usage"]["input_tokens"] + result["usage"]["output_tokens"]
                
                return AIResponse(
                    content=content,
                    provider="anthropic",
                    model=self.config.anthropic_model,
                    tokens_used=tokens
                )
            
            error_text = await response.text()
            raise Exception(f"Anthropic API error {response.status}: {error_text}")
    
    def _generate_local(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        """Generate local fallback response."""
        prompt_lower = prompt.lower()
        
        # Math responses
        if "2+2" in prompt_lower or "2 + 2" in prompt_lower:
            content = "2 + 2 = 4"
        elif "what is" in prompt_lower and any(op in prompt for op in ["+", "-", "*", "/"]):
            content = "I can help with basic math. For complex calculations, please configure an AI API key."
        
        # Greetings
        elif any(word in prompt_lower for word in ["hello", "hi", "hey"]):
            content = "Hello! I'm NOVA, your AI assistant. I'm running in local mode. Configure an AI API key for enhanced responses."
        
        # AI questions
        elif "artificial intelligence" in prompt_lower or " ai " in prompt_lower:
            content = "Artificial Intelligence (AI) is the simulation of human intelligence by machines, particularly computer systems. It includes learning, reasoning, and problem-solving capabilities."
        
        # Help
        elif "help" in prompt_lower or "what can you do" in prompt_lower:
            content = "I'm NOVA, your AI assistant. I can help with basic questions, math, and general information. For advanced AI capabilities, please configure an API key."
        
        # Test
        elif "test" in prompt_lower:
            content = "✅ NOVA is working! I'm currently running in local mode. Configure an AI API key for enhanced responses."
        
        # Default
        else:
            content = f"I understand you're asking about '{prompt}'. I'm currently running in local mode with limited capabilities. Please configure an AI API key for detailed responses."
        
        return AIResponse(
            content=content,
            provider="local",
            model="fallback",
            confidence=0.7
        )
    
    async def _generate_fallback(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        """Try fallback providers in order of preference."""
        providers = [
            (AIProvider.GEMINI, self.config.gemini_api_key),
            (AIProvider.OPENAI, self.config.openai_api_key),
            (AIProvider.ANTHROPIC, self.config.anthropic_api_key)
        ]
        
        for provider, api_key in providers:
            if api_key:
                try:
                    if provider == AIProvider.GEMINI:
                        return await self._generate_gemini(prompt, context, system_prompt)
                    elif provider == AIProvider.OPENAI:
                        return await self._generate_openai(prompt, context, system_prompt)
                    elif provider == AIProvider.ANTHROPIC:
                        return await self._generate_anthropic(prompt, context, system_prompt)
                except Exception as e:
                    self.logger.warning(f"Fallback provider {provider.value} failed: {e}")
                    continue
        
        # Final fallback to local
        return self._generate_local(prompt, context, system_prompt)
    
    def _build_prompt(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Build complete prompt with context and instructions."""
        parts = []
        
        if system_prompt:
            parts.append(f"System: {system_prompt}")
        
        if context:
            parts.append(f"Context: {context}")
        
        parts.append(f"User: {prompt}")
        
        return "\n\n".join(parts)
