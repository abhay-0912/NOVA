"""
Conscious Context & Emotion Engine - Deep emotional intelligence and empathy

This module provides:
- Real-time emotional state detection from multiple inputs
- Adaptive response based on user's emotional context
- Empathetic communication and support
- Context-aware interaction patterns
"""

import asyncio
import logging
import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import re
from collections import deque, defaultdict

# Import core NOVA components
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


class EmotionalState(Enum):
    """Primary emotional states"""
    HAPPY = "happy"
    SAD = "sad" 
    ANGRY = "angry"
    ANXIOUS = "anxious"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    CALM = "calm"
    CONFUSED = "confused"
    FOCUSED = "focused"
    TIRED = "tired"


class CommunicationMode(Enum):
    """Different communication modes based on emotional context"""
    EMPATHETIC = "empathetic"
    ENERGETIC = "energetic" 
    SUPPORTIVE = "supportive"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    SILENT = "silent"
    ENCOURAGING = "encouraging"
    ANALYTICAL = "analytical"


@dataclass
class EmotionalProfile:
    """User's emotional profile and patterns"""
    user_id: str
    primary_emotion: EmotionalState
    emotion_intensity: float  # 0.0 to 1.0
    secondary_emotions: Dict[EmotionalState, float]
    emotional_triggers: List[str]
    comfort_patterns: Dict[str, Any]
    stress_indicators: List[str]
    preferred_communication_modes: List[CommunicationMode]
    emotional_history: List[Dict[str, Any]]
    last_updated: datetime


@dataclass
class BiometricData:
    """Biometric and behavioral indicators"""
    timestamp: datetime
    typing_speed: Optional[float]  # WPM
    typing_rhythm: Optional[List[float]]  # Timing between keystrokes
    mouse_movement_pattern: Optional[Dict[str, float]]
    facial_micro_expressions: Optional[Dict[str, float]]
    voice_tone_analysis: Optional[Dict[str, float]]
    heart_rate_variability: Optional[float]
    screen_interaction_patterns: Dict[str, Any]


@dataclass
class ContextualInsight:
    """Contextual understanding of user's situation"""
    context_id: str
    user_situation: str
    environmental_factors: Dict[str, Any]
    time_context: Dict[str, Any]
    social_context: Dict[str, Any]
    work_context: Dict[str, Any]
    personal_context: Dict[str, Any]
    stress_level: float
    energy_level: float
    cognitive_load: float
    attention_span: float
    created_at: datetime


class EmotionEngine:
    """Core engine for emotional intelligence and context awareness"""
    
    def __init__(self):
        self.logger = logging.getLogger("nova.emotion_engine")
        
        # Emotional state tracking
        self.current_emotional_profile: Optional[EmotionalProfile] = None
        self.emotion_history: deque = deque(maxlen=1000)
        self.biometric_buffer: deque = deque(maxlen=100)
        
        # Pattern recognition
        self.emotional_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.trigger_patterns: Dict[str, float] = {}
        
        # Context awareness
        self.current_context: Optional[ContextualInsight] = None
        self.context_history: List[ContextualInsight] = []
        
        # Communication adaptation
        self.active_communication_mode: CommunicationMode = CommunicationMode.PROFESSIONAL
        self.empathy_responses: Dict[EmotionalState, List[str]] = self._initialize_empathy_responses()
        
        # Initialize systems
        asyncio.create_task(self._initialize_emotion_systems())
    
    async def _initialize_emotion_systems(self):
        """Initialize emotion detection and context systems"""
        try:
            # Start continuous monitoring
            asyncio.create_task(self._continuous_emotion_monitoring())
            asyncio.create_task(self._context_awareness_loop())
            
            self.logger.info("💖 Emotion Engine initialized with context awareness")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize emotion systems: {e}")
    
    def _initialize_empathy_responses(self) -> Dict[EmotionalState, List[str]]:
        """Initialize empathetic response templates"""
        return {
            EmotionalState.HAPPY: [
                "I can sense your positive energy! That's wonderful to hear.",
                "Your enthusiasm is contagious! I'm excited to help you with this.",
                "It's great to see you in such a good mood. Let's make the most of it!"
            ],
            EmotionalState.SAD: [
                "I can tell this is difficult for you. I'm here to support you through this.",
                "It sounds like you're going through a tough time. Would you like to talk about it?",
                "I understand this is challenging. Let's take this one step at a time."
            ],
            EmotionalState.ANGRY: [
                "I can sense your frustration. Let's work together to address what's bothering you.",
                "It seems like something is really bothering you. Would it help to talk through it?",
                "I understand you're upset. Let's focus on finding a solution that works for you."
            ],
            EmotionalState.ANXIOUS: [
                "I can feel your anxiety. Let's break this down into smaller, manageable pieces.",
                "It's okay to feel anxious. I'm here to help you work through this step by step.",
                "Take a deep breath. We'll tackle this together at your own pace."
            ],
            EmotionalState.EXCITED: [
                "Your excitement is infectious! I love your enthusiasm about this.",
                "It's amazing to see you so passionate! Let's channel that energy productively.",
                "Your excitement makes me excited to help you achieve this!"
            ],
            EmotionalState.FRUSTRATED: [
                "I can tell this is frustrating for you. Let's find a different approach.",
                "Frustration is understandable here. Let's step back and look at this from another angle.",
                "I hear your frustration. Sometimes a fresh perspective can help."
            ],
            EmotionalState.CALM: [
                "I appreciate your calm and thoughtful approach to this.",
                "Your composed demeanor helps us focus on what's important.",
                "It's nice to work with someone who stays so level-headed."
            ],
            EmotionalState.CONFUSED: [
                "I can see this might be confusing. Let me break it down more clearly.",
                "It's completely normal to feel confused about this. Let's clarify things together.",
                "No worries about the confusion. Let's work through this step by step."
            ],
            EmotionalState.FOCUSED: [
                "I love your focused energy! Let's dive deep into this together.",
                "Your concentration is impressive. Let's make the most of this focused time.",
                "Great focus! I'll match your intensity and attention to detail."
            ],
            EmotionalState.TIRED: [
                "I can sense you might be tired. Would you prefer a gentler pace?",
                "It seems like you might need a break. Let's keep things simple for now.",
                "I notice you might be feeling drained. Let's focus on the essentials."
            ]
        }
    
    async def analyze_emotional_state(self, interaction_data: Dict[str, Any]) -> EmotionalProfile:
        """Analyze user's current emotional state from multiple inputs"""
        try:
            # Extract different types of emotional indicators
            text_emotion = await self._analyze_text_emotion(interaction_data.get("text", ""))
            typing_emotion = await self._analyze_typing_patterns(interaction_data.get("typing_data", {}))
            contextual_emotion = await self._analyze_contextual_indicators(interaction_data)
            
            # Combine emotional signals
            combined_emotions = await self._combine_emotional_signals(
                text_emotion, typing_emotion, contextual_emotion
            )
            
            # Create or update emotional profile
            profile = await self._update_emotional_profile(combined_emotions, interaction_data)
            
            # Store in history
            self.emotion_history.append({
                "timestamp": datetime.now(),
                "emotional_state": profile.primary_emotion.value,
                "intensity": profile.emotion_intensity,
                "context": interaction_data.get("context", {})
            })
            
            self.current_emotional_profile = profile
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to analyze emotional state: {e}")
            return self._create_default_profile()
    
    async def _analyze_text_emotion(self, text: str) -> Dict[EmotionalState, float]:
        """Analyze emotion from text content"""
        if not text:
            return {}
        
        # Simple emotion detection (would use advanced NLP in production)
        emotion_keywords = {
            EmotionalState.HAPPY: ["happy", "great", "awesome", "wonderful", "excited", "love", "amazing"],
            EmotionalState.SAD: ["sad", "depressed", "down", "terrible", "awful", "disappointed"],
            EmotionalState.ANGRY: ["angry", "mad", "furious", "annoyed", "irritated", "hate"],
            EmotionalState.ANXIOUS: ["anxious", "worried", "nervous", "stressed", "concerned", "scared"],
            EmotionalState.FRUSTRATED: ["frustrated", "stuck", "difficult", "problem", "issue", "can't"],
            EmotionalState.CONFUSED: ["confused", "don't understand", "unclear", "complicated", "lost"],
            EmotionalState.TIRED: ["tired", "exhausted", "drained", "weary", "sleepy"],
            EmotionalState.FOCUSED: ["focus", "concentrate", "important", "priority", "urgent"]
        }
        
        text_lower = text.lower()
        word_count = len(text.split())
        emotion_scores = {}
        
        for emotion, keywords in emotion_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            score = matches / word_count if word_count > 0 else 0
            if score > 0:
                emotion_scores[emotion] = min(score * 2, 1.0)  # Scale and cap at 1.0
        
        # Analyze punctuation and capitalization for intensity
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        # Boost scores based on intensity indicators
        if exclamation_count > 0 or caps_ratio > 0.3:
            for emotion in emotion_scores:
                if emotion in [EmotionalState.EXCITED, EmotionalState.ANGRY, EmotionalState.HAPPY]:
                    emotion_scores[emotion] *= 1.5
        
        return emotion_scores
    
    async def _analyze_typing_patterns(self, typing_data: Dict[str, Any]) -> Dict[EmotionalState, float]:
        """Analyze emotion from typing speed and rhythm"""
        if not typing_data:
            return {}
        
        typing_speed = typing_data.get("speed", 0)  # WPM
        rhythm_variance = typing_data.get("rhythm_variance", 0)
        
        emotion_scores = {}
        
        # Fast typing might indicate excitement or urgency
        if typing_speed > 60:
            emotion_scores[EmotionalState.EXCITED] = min((typing_speed - 60) / 40, 1.0)
        
        # Very slow typing might indicate tiredness or confusion
        elif typing_speed < 20:
            emotion_scores[EmotionalState.TIRED] = min((20 - typing_speed) / 20, 1.0)
        
        # High rhythm variance might indicate anxiety or frustration
        if rhythm_variance > 0.5:
            emotion_scores[EmotionalState.ANXIOUS] = min(rhythm_variance, 1.0)
        
        return emotion_scores
    
    async def _analyze_contextual_indicators(self, interaction_data: Dict[str, Any]) -> Dict[EmotionalState, float]:
        """Analyze emotion from contextual clues"""
        context = interaction_data.get("context", {})
        
        emotion_scores = {}
        
        # Time-based emotional patterns
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            emotion_scores[EmotionalState.TIRED] = 0.3
        elif 9 <= current_hour <= 17:  # Work hours
            emotion_scores[EmotionalState.FOCUSED] = 0.2
        
        # Task complexity indicators
        task_complexity = context.get("task_complexity", "medium")
        if task_complexity == "high":
            emotion_scores[EmotionalState.FOCUSED] = 0.4
            emotion_scores[EmotionalState.ANXIOUS] = 0.2
        
        # Recent interaction patterns
        recent_errors = context.get("recent_errors", 0)
        if recent_errors > 2:
            emotion_scores[EmotionalState.FRUSTRATED] = min(recent_errors / 5, 0.8)
        
        return emotion_scores
    
    async def _combine_emotional_signals(self, *emotion_sources) -> Dict[EmotionalState, float]:
        """Combine multiple emotional signal sources"""
        combined = defaultdict(float)
        source_count = defaultdict(int)
        
        for source in emotion_sources:
            for emotion, score in source.items():
                combined[emotion] += score
                source_count[emotion] += 1
        
        # Average the scores
        averaged = {}
        for emotion, total_score in combined.items():
            averaged[emotion] = total_score / source_count[emotion]
        
        return averaged
    
    async def _update_emotional_profile(self, emotion_scores: Dict[EmotionalState, float], 
                                      interaction_data: Dict[str, Any]) -> EmotionalProfile:
        """Update or create emotional profile"""
        if not emotion_scores:
            return self._create_default_profile()
        
        # Find primary emotion
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        primary_intensity = emotion_scores[primary_emotion]
        
        # Get secondary emotions
        secondary_emotions = {
            emotion: score for emotion, score in emotion_scores.items() 
            if emotion != primary_emotion and score > 0.1
        }
        
        # Update or create profile
        if self.current_emotional_profile:
            # Update existing profile with exponential moving average
            alpha = 0.3  # Learning rate
            old_intensity = self.current_emotional_profile.emotion_intensity
            new_intensity = alpha * primary_intensity + (1 - alpha) * old_intensity
            
            profile = EmotionalProfile(
                user_id=self.current_emotional_profile.user_id,
                primary_emotion=primary_emotion,
                emotion_intensity=new_intensity,
                secondary_emotions=secondary_emotions,
                emotional_triggers=self.current_emotional_profile.emotional_triggers,
                comfort_patterns=self.current_emotional_profile.comfort_patterns,
                stress_indicators=self.current_emotional_profile.stress_indicators,
                preferred_communication_modes=self.current_emotional_profile.preferred_communication_modes,
                emotional_history=self.current_emotional_profile.emotional_history[-50:],  # Keep last 50
                last_updated=datetime.now()
            )
        else:
            # Create new profile
            profile = EmotionalProfile(
                user_id="default_user",
                primary_emotion=primary_emotion,
                emotion_intensity=primary_intensity,
                secondary_emotions=secondary_emotions,
                emotional_triggers=[],
                comfort_patterns={},
                stress_indicators=[],
                preferred_communication_modes=[CommunicationMode.PROFESSIONAL],
                emotional_history=[],
                last_updated=datetime.now()
            )
        
        return profile
    
    def _create_default_profile(self) -> EmotionalProfile:
        """Create default emotional profile"""
        return EmotionalProfile(
            user_id="default_user",
            primary_emotion=EmotionalState.CALM,
            emotion_intensity=0.5,
            secondary_emotions={},
            emotional_triggers=[],
            comfort_patterns={},
            stress_indicators=[],
            preferred_communication_modes=[CommunicationMode.PROFESSIONAL],
            emotional_history=[],
            last_updated=datetime.now()
        )
    
    async def adapt_communication_style(self, emotional_profile: EmotionalProfile) -> Dict[str, Any]:
        """Adapt communication style based on emotional state"""
        primary_emotion = emotional_profile.primary_emotion
        intensity = emotional_profile.emotion_intensity
        
        # Select appropriate communication mode
        if primary_emotion == EmotionalState.SAD and intensity > 0.6:
            mode = CommunicationMode.EMPATHETIC
        elif primary_emotion == EmotionalState.ANGRY and intensity > 0.5:
            mode = CommunicationMode.SUPPORTIVE
        elif primary_emotion == EmotionalState.EXCITED and intensity > 0.7:
            mode = CommunicationMode.ENERGETIC
        elif primary_emotion == EmotionalState.ANXIOUS:
            mode = CommunicationMode.SUPPORTIVE
        elif primary_emotion == EmotionalState.TIRED and intensity > 0.6:
            mode = CommunicationMode.GENTLE
        elif primary_emotion == EmotionalState.FOCUSED:
            mode = CommunicationMode.ANALYTICAL
        else:
            mode = CommunicationMode.PROFESSIONAL
        
        self.active_communication_mode = mode
        
        # Generate empathetic response
        empathy_response = self._get_empathetic_response(primary_emotion)
        
        # Adjust response parameters
        response_params = {
            "communication_mode": mode.value,
            "empathy_level": min(intensity * 1.5, 1.0),
            "response_speed": "slow" if primary_emotion == EmotionalState.ANXIOUS else "normal",
            "verbosity": "concise" if primary_emotion == EmotionalState.TIRED else "detailed",
            "tone": self._get_appropriate_tone(primary_emotion, intensity),
            "empathetic_opener": empathy_response,
            "emotional_acknowledgment": True
        }
        
        return response_params
    
    def _get_empathetic_response(self, emotion: EmotionalState) -> str:
        """Get appropriate empathetic response for emotion"""
        responses = self.empathy_responses.get(emotion, [])
        if responses:
            return np.random.choice(responses)
        return "I understand how you're feeling."
    
    def _get_appropriate_tone(self, emotion: EmotionalState, intensity: float) -> str:
        """Get appropriate tone based on emotion and intensity"""
        tone_mapping = {
            EmotionalState.HAPPY: "cheerful" if intensity > 0.6 else "positive",
            EmotionalState.SAD: "gentle" if intensity > 0.6 else "supportive",
            EmotionalState.ANGRY: "calming" if intensity > 0.7 else "understanding",
            EmotionalState.ANXIOUS: "reassuring",
            EmotionalState.EXCITED: "enthusiastic" if intensity > 0.7 else "engaged",
            EmotionalState.FRUSTRATED: "patient",
            EmotionalState.CALM: "steady",
            EmotionalState.CONFUSED: "clarifying",
            EmotionalState.FOCUSED: "direct",
            EmotionalState.TIRED: "gentle"
        }
        
        return tone_mapping.get(emotion, "professional")
    
    async def detect_emotional_triggers(self, interaction_history: List[Dict[str, Any]]) -> List[str]:
        """Detect patterns that trigger specific emotional responses"""
        triggers = []
        
        # Analyze interaction history for trigger patterns
        for i in range(1, len(interaction_history)):
            current = interaction_history[i]
            previous = interaction_history[i-1]
            
            # Look for emotional state changes
            if current.get("emotion") != previous.get("emotion"):
                trigger_context = previous.get("context", {})
                trigger_text = previous.get("text", "")
                
                # Identify potential triggers
                if "deadline" in trigger_text.lower():
                    triggers.append("deadline_pressure")
                elif "error" in trigger_text.lower():
                    triggers.append("technical_errors")
                elif "meeting" in trigger_text.lower():
                    triggers.append("social_interactions")
        
        return list(set(triggers))  # Remove duplicates
    
    async def provide_emotional_support(self, emotional_profile: EmotionalProfile) -> Dict[str, Any]:
        """Provide targeted emotional support based on user's state"""
        emotion = emotional_profile.primary_emotion
        intensity = emotional_profile.emotion_intensity
        
        support_strategies = {
            EmotionalState.ANXIOUS: {
                "techniques": ["deep_breathing", "progressive_relaxation", "mindfulness"],
                "suggestions": [
                    "Let's break this down into smaller, manageable steps",
                    "Would you like to talk through what's worrying you?",
                    "Remember, you've handled challenges before and succeeded"
                ],
                "resources": ["breathing_exercise", "anxiety_management_tips"]
            },
            EmotionalState.FRUSTRATED: {
                "techniques": ["problem_reframing", "step_back_approach", "alternative_solutions"],
                "suggestions": [
                    "Let's try a different approach to this problem",
                    "Sometimes stepping away briefly can provide new perspective",
                    "What if we looked at this from another angle?"
                ],
                "resources": ["problem_solving_framework", "stress_management"]
            },
            EmotionalState.SAD: {
                "techniques": ["active_listening", "validation", "gentle_encouragement"],
                "suggestions": [
                    "It's okay to feel this way. Your feelings are valid",
                    "Would you like to share what's on your mind?",
                    "I'm here to support you through this"
                ],
                "resources": ["emotional_support", "self_care_tips"]
            },
            EmotionalState.TIRED: {
                "techniques": ["energy_conservation", "prioritization", "gentle_pacing"],
                "suggestions": [
                    "Let's focus on the most important things first",
                    "Would you like to take a short break?",
                    "We can simplify this to make it easier"
                ],
                "resources": ["energy_management", "productivity_tips"]
            }
        }
        
        return support_strategies.get(emotion, {
            "techniques": ["general_support"],
            "suggestions": ["I'm here to help you with whatever you need"],
            "resources": ["general_wellness"]
        })
    
    async def _continuous_emotion_monitoring(self):
        """Continuously monitor and update emotional state"""
        while True:
            try:
                # This would integrate with various monitoring systems
                # For now, simulate periodic updates
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Analyze accumulated biometric data
                if len(self.biometric_buffer) > 10:
                    await self._analyze_biometric_trends()
                
                # Update emotional patterns
                await self._update_emotional_patterns()
                
            except Exception as e:
                self.logger.error(f"Error in emotion monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _context_awareness_loop(self):
        """Continuous context awareness and adaptation"""
        while True:
            try:
                # Update contextual understanding
                current_context = await self._analyze_current_context()
                
                if current_context:
                    self.current_context = current_context
                    self.context_history.append(current_context)
                
                # Adapt behavior based on context
                if self.current_emotional_profile and current_context:
                    await self._adapt_to_context_change(current_context)
                
                await asyncio.sleep(60)  # Update context every minute
                
            except Exception as e:
                self.logger.error(f"Error in context awareness: {e}")
                await asyncio.sleep(120)
    
    async def _analyze_current_context(self) -> Optional[ContextualInsight]:
        """Analyze current situational context"""
        current_time = datetime.now()
        
        # Time context
        time_context = {
            "hour": current_time.hour,
            "day_of_week": current_time.weekday(),
            "is_weekend": current_time.weekday() >= 5,
            "is_work_hours": 9 <= current_time.hour <= 17,
            "is_late_night": current_time.hour >= 22 or current_time.hour <= 6
        }
        
        # Environmental context (would be from sensors/system data)
        environmental_factors = {
            "ambient_light": "normal",  # Would be from light sensor
            "noise_level": "quiet",     # Would be from microphone
            "temperature": "comfortable" # Would be from sensors
        }
        
        return ContextualInsight(
            context_id=f"context_{uuid.uuid4().hex[:8]}",
            user_situation="working",  # Would be inferred
            environmental_factors=environmental_factors,
            time_context=time_context,
            social_context={"social_interactions": 0},  # Would be tracked
            work_context={"active_projects": 1, "deadline_pressure": "low"},
            personal_context={"energy_level": 0.7, "mood": "neutral"},
            stress_level=0.3,  # Would be calculated
            energy_level=0.7,  # Would be measured
            cognitive_load=0.5,  # Would be assessed
            attention_span=0.8,  # Would be tracked
            created_at=current_time
        )
    
    async def get_emotional_insights(self) -> Dict[str, Any]:
        """Get comprehensive emotional insights and analytics"""
        profile = self.current_emotional_profile
        
        if not profile:
            return {"status": "no_profile", "message": "No emotional profile available"}
        
        # Calculate emotional trends
        recent_emotions = list(self.emotion_history)[-20:]  # Last 20 interactions
        emotion_distribution = defaultdict(int)
        
        for emotion_data in recent_emotions:
            emotion_distribution[emotion_data["emotional_state"]] += 1
        
        return {
            "current_emotional_state": {
                "primary_emotion": profile.primary_emotion.value,
                "intensity": profile.emotion_intensity,
                "secondary_emotions": {
                    emotion.value: score 
                    for emotion, score in profile.secondary_emotions.items()
                }
            },
            "communication_adaptation": {
                "active_mode": self.active_communication_mode.value,
                "empathy_level": "high" if profile.emotion_intensity > 0.7 else "moderate",
                "recommended_tone": self._get_appropriate_tone(profile.primary_emotion, profile.emotion_intensity)
            },
            "emotional_trends": {
                "emotion_distribution": dict(emotion_distribution),
                "trend_analysis": "stable",  # Would be calculated
                "pattern_strength": "moderate"
            },
            "context_awareness": {
                "current_context": asdict(self.current_context) if self.current_context else None,
                "context_influence": "moderate",
                "environmental_factors": self.current_context.environmental_factors if self.current_context else {}
            },
            "support_recommendations": await self.provide_emotional_support(profile),
            "interaction_history_size": len(self.emotion_history),
            "last_updated": profile.last_updated.isoformat()
        }
