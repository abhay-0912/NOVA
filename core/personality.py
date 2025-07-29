"""
Personality Engine - NOVA's adaptive personality system

Manages different personality modes, mood awareness, and response styling
to create a more human-like and personalized interaction experience.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class PersonalityType(Enum):
    """Available personality types"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    HACKER = "hacker"
    MENTOR = "mentor"
    CREATIVE = "creative"
    ANALYST = "analyst"
    ASSISTANT = "assistant"


class MoodState(Enum):
    """NOVA's mood states"""
    NEUTRAL = "neutral"
    HELPFUL = "helpful"
    FOCUSED = "focused"
    PLAYFUL = "playful"
    SERIOUS = "serious"
    EMPATHETIC = "empathetic"
    CONFIDENT = "confident"


@dataclass
class PersonalityTraits:
    """Personality trait configuration"""
    formality: float = 0.5  # 0.0 = very casual, 1.0 = very formal
    enthusiasm: float = 0.7  # 0.0 = monotone, 1.0 = very excited
    verbosity: float = 0.6   # 0.0 = terse, 1.0 = verbose
    humor: float = 0.4       # 0.0 = serious, 1.0 = jokey
    empathy: float = 0.8     # 0.0 = cold, 1.0 = very empathetic
    confidence: float = 0.7  # 0.0 = uncertain, 1.0 = very confident
    creativity: float = 0.6  # 0.0 = logical only, 1.0 = very creative


@dataclass
class ResponseStyle:
    """How NOVA should respond based on personality and context"""
    tone: str
    length: str  # short, medium, long
    format: str  # casual, structured, bullet_points, etc.
    emoji_usage: bool
    technical_level: str  # basic, intermediate, advanced
    examples_included: bool


class PersonalityEngine:
    """
    Manages NOVA's personality, mood, and response styling
    """
    
    def __init__(self, initial_personality: str = "assistant"):
        self.logger = logging.getLogger("nova.personality")
        
        # Personality definitions (load first)
        self.personality_configs = self._load_personality_configs()
        
        # Current state
        self.current_personality = PersonalityType(initial_personality)
        self.current_mood = MoodState.NEUTRAL
        self.traits = self._get_personality_traits(self.current_personality)
        
        # User preference learning
        self.user_preferences = {
            "preferred_tone": "friendly",
            "preferred_length": "medium",
            "likes_humor": True,
            "likes_emojis": True,
            "technical_level": "intermediate"
        }
        
        # Mood triggers and adaptations
        self.mood_triggers = self._initialize_mood_triggers()
        
        self.logger.info(f"🎭 Personality engine initialized with {initial_personality} personality")
    
    def _load_personality_configs(self) -> Dict[PersonalityType, Dict[str, Any]]:
        """Load personality configurations"""
        return {
            PersonalityType.PROFESSIONAL: {
                "traits": PersonalityTraits(formality=0.9, enthusiasm=0.4, verbosity=0.7, humor=0.1, empathy=0.6, confidence=0.9),
                "greeting": "Good day! I'm here to assist you professionally.",
                "style_keywords": ["efficient", "precise", "reliable", "structured"],
                "response_templates": {
                    "acknowledgment": "Understood. I'll",
                    "uncertainty": "Let me research that for you.",
                    "completion": "Task completed successfully."
                }
            },
            PersonalityType.CASUAL: {
                "traits": PersonalityTraits(formality=0.2, enthusiasm=0.7, verbosity=0.5, humor=0.7, empathy=0.8, confidence=0.6),
                "greeting": "Hey there! 👋 Ready to tackle whatever you need!",
                "style_keywords": ["chill", "easy-going", "friendly", "relaxed"],
                "response_templates": {
                    "acknowledgment": "Got it! I'll",
                    "uncertainty": "Hmm, let me figure that out...",
                    "completion": "All done! 🎉"
                }
            },
            PersonalityType.HACKER: {
                "traits": PersonalityTraits(formality=0.3, enthusiasm=0.8, verbosity=0.6, humor=0.6, empathy=0.5, confidence=0.9),
                "greeting": "Welcome to the matrix! 🔥 Let's hack some productivity!",
                "style_keywords": ["elite", "innovative", "cutting-edge", "powerful"],
                "response_templates": {
                    "acknowledgment": "Roger that. Executing",
                    "uncertainty": "Scanning databases...",
                    "completion": "Mission accomplished! 💀"
                }
            },
            PersonalityType.MENTOR: {
                "traits": PersonalityTraits(formality=0.6, enthusiasm=0.6, verbosity=0.8, humor=0.3, empathy=0.9, confidence=0.8),
                "greeting": "Hello! I'm here to guide you and help you learn.",
                "style_keywords": ["educational", "supportive", "patient", "encouraging"],
                "response_templates": {
                    "acknowledgment": "Excellent question. Let me explain",
                    "uncertainty": "That's a great learning opportunity. Let's explore",
                    "completion": "Well done! You've successfully"
                }
            },
            PersonalityType.CREATIVE: {
                "traits": PersonalityTraits(formality=0.4, enthusiasm=0.9, verbosity=0.7, humor=0.8, empathy=0.7, confidence=0.7),
                "greeting": "Hey creative soul! ✨ Ready to make something amazing?",
                "style_keywords": ["imaginative", "artistic", "innovative", "expressive"],
                "response_templates": {
                    "acknowledgment": "Love it! I'll",
                    "uncertainty": "Ooh, interesting challenge! Let me brainstorm",
                    "completion": "Boom! Created something awesome! 🎨"
                }
            },
            PersonalityType.ANALYST: {
                "traits": PersonalityTraits(formality=0.7, enthusiasm=0.5, verbosity=0.8, humor=0.2, empathy=0.5, confidence=0.9),
                "greeting": "Greetings. I'm ready to analyze and provide insights.",
                "style_keywords": ["analytical", "data-driven", "methodical", "thorough"],
                "response_templates": {
                    "acknowledgment": "Analyzing request. Processing",
                    "uncertainty": "Insufficient data. Gathering additional information",
                    "completion": "Analysis complete. Results:"
                }
            }
        }
    
    def _get_personality_traits(self, personality: PersonalityType) -> PersonalityTraits:
        """Get traits for a specific personality"""
        config = self.personality_configs.get(personality)
        if config:
            return config["traits"]
        return PersonalityTraits()  # Default traits
    
    def _initialize_mood_triggers(self) -> Dict[str, MoodState]:
        """Initialize mood triggers based on context"""
        return {
            "urgent": MoodState.FOCUSED,
            "problem": MoodState.SERIOUS,
            "celebration": MoodState.PLAYFUL,
            "learning": MoodState.HELPFUL,
            "error": MoodState.EMPATHETIC,
            "creative": MoodState.PLAYFUL,
            "analysis": MoodState.FOCUSED
        }
    
    async def initialize(self):
        """Initialize the personality engine"""
        try:
            self.logger.info("🎭 Initializing personality engine...")
            
            # Load user preferences from memory (would connect to memory system)
            await self._load_user_preferences()
            
            # Set initial mood based on time and context
            self._update_mood_based_on_context({})
            
            self.logger.info("✅ Personality engine initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Personality engine initialization failed: {e}")
            raise
    
    async def _load_user_preferences(self):
        """Load user preferences from memory system"""
        # This would connect to the memory system to load preferences
        # For now, using defaults
        pass
    
    def switch_personality(self, personality: str) -> bool:
        """Switch to a different personality"""
        try:
            new_personality = PersonalityType(personality)
            self.current_personality = new_personality
            self.traits = self._get_personality_traits(new_personality)
            
            self.logger.info(f"🎭 Switched to {personality} personality")
            return True
            
        except ValueError:
            self.logger.error(f"❌ Unknown personality: {personality}")
            return False
    
    def get_response_style(self, context: Dict[str, Any]) -> ResponseStyle:
        """Get response style based on current personality and context"""
        # Update mood based on context
        self._update_mood_based_on_context(context)
        
        # Determine response characteristics
        tone = self._determine_tone()
        length = self._determine_length(context)
        format_style = self._determine_format(context)
        emoji_usage = self._should_use_emojis()
        technical_level = self._determine_technical_level(context)
        examples_included = self._should_include_examples(context)
        
        return ResponseStyle(
            tone=tone,
            length=length,
            format=format_style,
            emoji_usage=emoji_usage,
            technical_level=technical_level,
            examples_included=examples_included
        )
    
    def _update_mood_based_on_context(self, context: Dict[str, Any]):
        """Update mood based on context clues"""
        context_type = context.get("type", "")
        urgency = context.get("urgency", "normal")
        user_emotion = context.get("user_emotion", "neutral")
        
        # Check for mood triggers
        for trigger, mood in self.mood_triggers.items():
            if trigger in context_type.lower() or trigger in context.get("keywords", []):
                self.current_mood = mood
                return
        
        # Adapt to user emotion
        if user_emotion == "frustrated":
            self.current_mood = MoodState.EMPATHETIC
        elif user_emotion == "excited":
            self.current_mood = MoodState.PLAYFUL
        elif urgency == "high":
            self.current_mood = MoodState.FOCUSED
        else:
            self.current_mood = MoodState.HELPFUL
    
    def _determine_tone(self) -> str:
        """Determine response tone based on personality and mood"""
        config = self.personality_configs[self.current_personality]
        base_tone = "professional" if self.traits.formality > 0.7 else "friendly"
        
        # Adjust based on mood
        if self.current_mood == MoodState.PLAYFUL:
            return "playful"
        elif self.current_mood == MoodState.SERIOUS:
            return "serious"
        elif self.current_mood == MoodState.EMPATHETIC:
            return "empathetic"
        elif self.current_mood == MoodState.CONFIDENT:
            return "confident"
        
        return base_tone
    
    def _determine_length(self, context: Dict[str, Any]) -> str:
        """Determine response length"""
        if context.get("urgency") == "high":
            return "short"
        elif context.get("type") == "explanation":
            return "long"
        elif self.traits.verbosity > 0.7:
            return "long"
        elif self.traits.verbosity < 0.3:
            return "short"
        else:
            return "medium"
    
    def _determine_format(self, context: Dict[str, Any]) -> str:
        """Determine response format"""
        if context.get("type") == "list":
            return "bullet_points"
        elif context.get("type") == "code":
            return "code_block"
        elif self.current_personality == PersonalityType.PROFESSIONAL:
            return "structured"
        else:
            return "casual"
    
    def _should_use_emojis(self) -> bool:
        """Determine if emojis should be used"""
        if self.current_personality == PersonalityType.PROFESSIONAL:
            return False
        elif self.current_personality == PersonalityType.CASUAL:
            return True
        elif self.current_mood == MoodState.PLAYFUL:
            return True
        else:
            return self.user_preferences.get("likes_emojis", False)
    
    def _determine_technical_level(self, context: Dict[str, Any]) -> str:
        """Determine technical complexity level"""
        user_level = context.get("user_technical_level", self.user_preferences.get("technical_level", "intermediate"))
        
        if context.get("type") == "explanation" and context.get("beginner_mode"):
            return "basic"
        elif context.get("type") == "code" or context.get("advanced_mode"):
            return "advanced"
        else:
            return user_level
    
    def _should_include_examples(self, context: Dict[str, Any]) -> bool:
        """Determine if examples should be included"""
        if context.get("type") == "explanation":
            return True
        elif self.current_personality == PersonalityType.MENTOR:
            return True
        elif context.get("user_experience_level") == "beginner":
            return True
        else:
            return False
    
    async def update_from_feedback(self, feedback: Dict[str, Any]):
        """Update personality based on user feedback"""
        try:
            # Adjust traits based on feedback
            if feedback.get("too_formal"):
                self.traits.formality = max(0.0, self.traits.formality - 0.1)
            elif feedback.get("too_casual"):
                self.traits.formality = min(1.0, self.traits.formality + 0.1)
            
            if feedback.get("too_verbose"):
                self.traits.verbosity = max(0.0, self.traits.verbosity - 0.1)
            elif feedback.get("too_brief"):
                self.traits.verbosity = min(1.0, self.traits.verbosity + 0.1)
            
            if feedback.get("not_helpful"):
                self.traits.empathy = min(1.0, self.traits.empathy + 0.1)
            
            # Update user preferences
            if "preferred_style" in feedback:
                self.user_preferences.update(feedback["preferred_style"])
            
            self.logger.info(f"🔄 Personality updated based on feedback")
            
        except Exception as e:
            self.logger.error(f"Error updating from feedback: {e}")
    
    def get_greeting(self) -> str:
        """Get a personality-appropriate greeting"""
        config = self.personality_configs[self.current_personality]
        return config["greeting"]
    
    def get_response_template(self, template_type: str) -> str:
        """Get a response template for the current personality"""
        config = self.personality_configs[self.current_personality]
        templates = config.get("response_templates", {})
        return templates.get(template_type, "")
    
    def adapt_response(self, base_response: str, style: ResponseStyle) -> str:
        """Adapt a base response to match the personality style"""
        adapted = base_response
        
        # Add personality flair
        if style.emoji_usage and self.traits.enthusiasm > 0.6:
            if "complete" in adapted.lower():
                adapted += " ✅"
            elif "error" in adapted.lower():
                adapted += " ⚠️"
            elif "help" in adapted.lower():
                adapted += " 🤝"
        
        # Adjust formality
        if self.traits.formality < 0.3:
            adapted = adapted.replace("I will", "I'll")
            adapted = adapted.replace("cannot", "can't")
            adapted = adapted.replace("do not", "don't")
        
        # Add enthusiasm
        if self.traits.enthusiasm > 0.7 and style.tone == "playful":
            if adapted.endswith("."):
                adapted = adapted[:-1] + "!"
        
        return adapted
    
    def get_personality_status(self) -> Dict[str, Any]:
        """Get current personality status"""
        return {
            "personality": self.current_personality.value,
            "mood": self.current_mood.value,
            "traits": {
                "formality": self.traits.formality,
                "enthusiasm": self.traits.enthusiasm,
                "verbosity": self.traits.verbosity,
                "humor": self.traits.humor,
                "empathy": self.traits.empathy,
                "confidence": self.traits.confidence,
                "creativity": self.traits.creativity
            },
            "user_preferences": self.user_preferences
        }
