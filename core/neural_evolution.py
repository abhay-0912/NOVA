"""
NOVA Neural Evolution Engine - Self-Learning Intelligence Core

This module implements lifelong learning capabilities that allow NOVA to:
- Continuously learn from user interactions and patterns
- Self-improve agents through performance analysis
- Implement reinforcement learning from human feedback (RLHF)
- Create a growing digital twin of the user's mind
"""

import asyncio
import logging
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import sqlite3
from pathlib import Path

# Import core NOVA components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.memory import MemorySystem


@dataclass
class LearningPattern:
    """Represents a learned pattern from user behavior"""
    pattern_id: str
    pattern_type: str  # habit, preference, style, workflow
    confidence: float
    frequency: int
    last_observed: datetime
    context: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class AgentPerformanceMetric:
    """Tracks agent performance for self-improvement"""
    agent_id: str
    task_type: str
    success_rate: float
    response_time: float
    user_satisfaction: float
    improvement_suggestions: List[str]
    timestamp: datetime


@dataclass
class UserInteractionProfile:
    """Deep user profile built from continuous learning"""
    user_id: str
    communication_style: Dict[str, float]  # formal, casual, technical, emotional
    work_patterns: Dict[str, Any]
    preferences: Dict[str, Any]
    expertise_areas: List[str]
    learning_speed: float
    typical_workflows: List[Dict[str, Any]]
    emotional_patterns: Dict[str, float]
    updated_at: datetime


class NeuroEvolutionEngine:
    """Core engine for NOVA's self-learning and evolution capabilities"""
    
    def __init__(self, memory_system: MemorySystem):
        self.memory = memory_system
        self.logger = logging.getLogger("nova.evolution")
        
        # Learning databases
        self.patterns_db = Path("data/learning_patterns.db")
        self.performance_db = Path("data/agent_performance.db")
        
        # Learning parameters
        self.learning_rate = 0.01
        self.pattern_threshold = 0.75
        self.adaptation_cycles = 0
        
        # Pattern recognition
        self.user_patterns: Dict[str, LearningPattern] = {}
        self.agent_metrics: Dict[str, List[AgentPerformanceMetric]] = defaultdict(list)
        self.user_profile: Optional[UserInteractionProfile] = None
        
        # Self-improvement queue
        self.improvement_queue: List[Dict[str, Any]] = []
        
        # Initialize databases
        asyncio.create_task(self._initialize_learning_systems())
    
    async def _initialize_learning_systems(self):
        """Initialize the learning and evolution systems"""
        try:
            # Create learning databases
            await self._create_learning_databases()
            
            # Load existing patterns
            await self._load_learning_history()
            
            # Start continuous learning loop
            asyncio.create_task(self._continuous_learning_loop())
            
            self.logger.info("🧠 Neural Evolution Engine initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize evolution engine: {e}")
    
    async def _create_learning_databases(self):
        """Create SQLite databases for learning data"""
        patterns_conn = sqlite3.connect(self.patterns_db)
        patterns_conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT,
                confidence REAL,
                frequency INTEGER,
                last_observed TEXT,
                context TEXT,
                metadata TEXT
            )
        """)
        patterns_conn.close()
        
        performance_conn = sqlite3.connect(self.performance_db)
        performance_conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT,
                task_type TEXT,
                success_rate REAL,
                response_time REAL,
                user_satisfaction REAL,
                improvement_suggestions TEXT,
                timestamp TEXT
            )
        """)
        performance_conn.close()
    
    async def observe_interaction(self, interaction_data: Dict[str, Any]):
        """Learn from user interactions in real-time"""
        try:
            # Extract patterns from interaction
            patterns = await self._extract_patterns(interaction_data)
            
            # Update user profile
            await self._update_user_profile(interaction_data)
            
            # Learn from agent performance
            if "agent_response" in interaction_data:
                await self._learn_from_agent_performance(interaction_data)
            
            # Detect new behavioral patterns
            await self._detect_new_patterns(patterns)
            
            self.logger.debug(f"Learned from interaction: {len(patterns)} patterns extracted")
            
        except Exception as e:
            self.logger.error(f"Failed to learn from interaction: {e}")
    
    async def _extract_patterns(self, interaction: Dict[str, Any]) -> List[LearningPattern]:
        """Extract behavioral patterns from user interactions"""
        patterns = []
        
        # Communication style patterns
        if "user_message" in interaction:
            comm_pattern = await self._analyze_communication_style(interaction["user_message"])
            if comm_pattern:
                patterns.append(comm_pattern)
        
        # Workflow patterns
        if "task_sequence" in interaction:
            workflow_pattern = await self._analyze_workflow_pattern(interaction["task_sequence"])
            if workflow_pattern:
                patterns.append(workflow_pattern)
        
        # Preference patterns
        if "user_choices" in interaction:
            pref_pattern = await self._analyze_preference_pattern(interaction["user_choices"])
            if pref_pattern:
                patterns.append(pref_pattern)
        
        # Temporal patterns (when user is most active/productive)
        time_pattern = await self._analyze_temporal_pattern(interaction)
        if time_pattern:
            patterns.append(time_pattern)
        
        return patterns
    
    async def _analyze_communication_style(self, message: str) -> Optional[LearningPattern]:
        """Analyze user's communication style and tone"""
        # Simple analysis - in production would use NLP models
        style_indicators = {
            "formal": len([w for w in message.split() if w in ["please", "thank you", "would", "could"]]),
            "casual": len([w for w in message.split() if w in ["hey", "yeah", "cool", "awesome"]]),
            "technical": len([w for w in message.split() if w in ["function", "algorithm", "database", "API"]]),
            "urgent": len([w for w in message.split() if w in ["urgent", "ASAP", "quickly", "now"]])
        }
        
        dominant_style = max(style_indicators, key=style_indicators.get)
        confidence = style_indicators[dominant_style] / len(message.split()) if message.split() else 0
        
        if confidence > 0.1:  # Threshold for pattern recognition
            return LearningPattern(
                pattern_id=f"comm_style_{datetime.now().isoformat()}",
                pattern_type="communication_style",
                confidence=confidence,
                frequency=1,
                last_observed=datetime.now(),
                context={"style": dominant_style, "message_length": len(message)},
                metadata={"indicators": style_indicators}
            )
        return None
    
    async def _analyze_workflow_pattern(self, task_sequence: List[str]) -> Optional[LearningPattern]:
        """Analyze user's workflow patterns"""
        # Look for common task sequences
        sequence_key = " -> ".join(task_sequence)
        
        return LearningPattern(
            pattern_id=f"workflow_{hash(sequence_key)}",
            pattern_type="workflow",
            confidence=0.8,
            frequency=1,
            last_observed=datetime.now(),
            context={"sequence": task_sequence, "length": len(task_sequence)},
            metadata={"workflow_type": "task_sequence"}
        )
    
    async def _update_user_profile(self, interaction: Dict[str, Any]):
        """Update the comprehensive user interaction profile"""
        if not self.user_profile:
            self.user_profile = UserInteractionProfile(
                user_id="default_user",
                communication_style={},
                work_patterns={},
                preferences={},
                expertise_areas=[],
                learning_speed=1.0,
                typical_workflows=[],
                emotional_patterns={},
                updated_at=datetime.now()
            )
        
        # Update communication style
        if "user_message" in interaction:
            await self._update_communication_profile(interaction["user_message"])
        
        # Update work patterns
        current_hour = datetime.now().hour
        if "task_type" in interaction:
            task_type = interaction["task_type"]
            if "hourly_activity" not in self.user_profile.work_patterns:
                self.user_profile.work_patterns["hourly_activity"] = defaultdict(int)
            self.user_profile.work_patterns["hourly_activity"][current_hour] += 1
        
        self.user_profile.updated_at = datetime.now()
    
    async def _update_communication_profile(self, message: str):
        """Update user's communication style profile"""
        # Analyze formality, emotion, complexity
        word_count = len(message.split())
        
        # Simple heuristics - would use advanced NLP in production
        formality_score = len([w for w in message.lower().split() 
                              if w in ["please", "thank", "would", "could", "may"]]) / word_count
        
        emotion_score = len([w for w in message.lower().split() 
                            if w in ["love", "hate", "excited", "frustrated", "happy", "sad"]]) / word_count
        
        # Update profile with exponential moving average
        alpha = 0.1  # Learning rate
        if "formality" not in self.user_profile.communication_style:
            self.user_profile.communication_style["formality"] = formality_score
        else:
            current = self.user_profile.communication_style["formality"]
            self.user_profile.communication_style["formality"] = alpha * formality_score + (1 - alpha) * current
        
        if "emotion" not in self.user_profile.communication_style:
            self.user_profile.communication_style["emotion"] = emotion_score
        else:
            current = self.user_profile.communication_style["emotion"]
            self.user_profile.communication_style["emotion"] = alpha * emotion_score + (1 - alpha) * current
    
    async def _learn_from_agent_performance(self, interaction: Dict[str, Any]):
        """Learn from how well agents performed on tasks"""
        agent_id = interaction.get("agent_id")
        task_type = interaction.get("task_type")
        response_time = interaction.get("response_time", 0)
        user_feedback = interaction.get("user_feedback", {})
        
        # Calculate performance metrics
        success_rate = 1.0 if user_feedback.get("successful", True) else 0.0
        satisfaction = user_feedback.get("satisfaction_score", 0.5)
        
        # Create performance metric
        metric = AgentPerformanceMetric(
            agent_id=agent_id,
            task_type=task_type,
            success_rate=success_rate,
            response_time=response_time,
            user_satisfaction=satisfaction,
            improvement_suggestions=user_feedback.get("suggestions", []),
            timestamp=datetime.now()
        )
        
        # Store and analyze
        self.agent_metrics[agent_id].append(metric)
        
        # Trigger self-improvement if performance is declining
        if len(self.agent_metrics[agent_id]) >= 10:
            await self._analyze_agent_for_improvement(agent_id)
    
    async def _analyze_agent_for_improvement(self, agent_id: str):
        """Analyze agent performance and suggest improvements"""
        recent_metrics = self.agent_metrics[agent_id][-10:]  # Last 10 interactions
        
        avg_success = sum(m.success_rate for m in recent_metrics) / len(recent_metrics)
        avg_satisfaction = sum(m.user_satisfaction for m in recent_metrics) / len(recent_metrics)
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        
        # Identify improvement areas
        improvements = []
        
        if avg_success < 0.8:
            improvements.append("Improve task success rate through better error handling")
        
        if avg_satisfaction < 0.7:
            improvements.append("Enhance response quality and user satisfaction")
        
        if avg_response_time > 5.0:  # 5 seconds threshold
            improvements.append("Optimize response time and efficiency")
        
        if improvements:
            improvement_task = {
                "agent_id": agent_id,
                "improvements": improvements,
                "priority": "high" if avg_success < 0.6 else "medium",
                "suggested_at": datetime.now()
            }
            self.improvement_queue.append(improvement_task)
            
            self.logger.info(f"🔧 Agent {agent_id} queued for improvement: {improvements}")
    
    async def evolve_agent(self, agent_id: str, improvement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evolve an agent based on learning data"""
        try:
            # Get agent performance history
            performance_history = self.agent_metrics.get(agent_id, [])
            
            # Analyze failure patterns
            failure_patterns = await self._analyze_failure_patterns(performance_history)
            
            # Generate improved agent logic
            evolution_strategy = await self._generate_evolution_strategy(
                agent_id, failure_patterns, improvement_data
            )
            
            # Apply evolutionary changes
            evolved_agent = await self._apply_evolution_strategy(agent_id, evolution_strategy)
            
            self.adaptation_cycles += 1
            
            return {
                "agent_id": agent_id,
                "evolution_applied": True,
                "improvements": evolution_strategy.get("improvements", []),
                "expected_benefits": evolution_strategy.get("benefits", []),
                "adaptation_cycle": self.adaptation_cycles,
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to evolve agent {agent_id}: {e}")
            return {"agent_id": agent_id, "evolution_applied": False, "error": str(e)}
    
    async def _analyze_failure_patterns(self, performance_history: List[AgentPerformanceMetric]) -> Dict[str, Any]:
        """Analyze patterns in agent failures to identify improvement areas"""
        failures = [m for m in performance_history if m.success_rate < 0.5]
        
        if not failures:
            return {"pattern": "no_failures", "confidence": 1.0}
        
        # Group failures by task type
        failure_by_task = defaultdict(list)
        for failure in failures:
            failure_by_task[failure.task_type].append(failure)
        
        # Find most problematic task types
        problem_tasks = {
            task: len(failures) / len([m for m in performance_history if m.task_type == task])
            for task, failures in failure_by_task.items()
        }
        
        return {
            "pattern": "task_specific_failures",
            "problem_tasks": problem_tasks,
            "total_failures": len(failures),
            "confidence": min(len(failures) / 10, 1.0)
        }
    
    async def _generate_evolution_strategy(self, agent_id: str, failure_patterns: Dict[str, Any], 
                                         improvement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategy for evolving the agent"""
        strategy = {
            "agent_id": agent_id,
            "improvements": [],
            "benefits": [],
            "implementation": []
        }
        
        # Based on failure patterns, suggest improvements
        if failure_patterns.get("pattern") == "task_specific_failures":
            problem_tasks = failure_patterns.get("problem_tasks", {})
            
            for task_type, failure_rate in problem_tasks.items():
                if failure_rate > 0.3:  # 30% failure rate threshold
                    strategy["improvements"].append(f"Enhance {task_type} handling logic")
                    strategy["benefits"].append(f"Reduce {task_type} failure rate by ~50%")
                    strategy["implementation"].append({
                        "type": "logic_enhancement",
                        "target": task_type,
                        "method": "reinforcement_learning"
                    })
        
        # Add general improvements based on user feedback
        user_suggestions = improvement_data.get("user_feedback", {}).get("suggestions", [])
        for suggestion in user_suggestions:
            strategy["improvements"].append(f"User-requested: {suggestion}")
            strategy["benefits"].append("Improved user satisfaction")
        
        return strategy
    
    async def _apply_evolution_strategy(self, agent_id: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the evolution strategy to improve the agent"""
        # This would modify the actual agent code/logic in production
        # For now, we simulate the evolution
        
        evolved_capabilities = []
        
        for improvement in strategy.get("implementation", []):
            if improvement["type"] == "logic_enhancement":
                evolved_capabilities.append(f"Enhanced {improvement['target']} processing")
            elif improvement["type"] == "new_capability":
                evolved_capabilities.append(f"Added {improvement['capability']}")
        
        return {
            "agent_id": agent_id,
            "evolved_capabilities": evolved_capabilities,
            "version": f"{self.adaptation_cycles + 1}.0",
            "evolution_timestamp": datetime.now().isoformat()
        }
    
    async def _continuous_learning_loop(self):
        """Continuous background learning and adaptation"""
        while True:
            try:
                # Process improvement queue
                if self.improvement_queue:
                    improvement_task = self.improvement_queue.pop(0)
                    await self.evolve_agent(
                        improvement_task["agent_id"],
                        improvement_task
                    )
                
                # Analyze patterns for insights
                await self._analyze_accumulated_patterns()
                
                # Save learning progress
                await self._save_learning_state()
                
                # Wait before next learning cycle
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in continuous learning loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _analyze_accumulated_patterns(self):
        """Analyze accumulated patterns for deeper insights"""
        if len(self.user_patterns) < 10:
            return  # Need more data
        
        # Group patterns by type
        pattern_groups = defaultdict(list)
        for pattern in self.user_patterns.values():
            pattern_groups[pattern.pattern_type].append(pattern)
        
        # Look for meta-patterns
        insights = {}
        for pattern_type, patterns in pattern_groups.items():
            avg_confidence = sum(p.confidence for p in patterns) / len(patterns)
            total_frequency = sum(p.frequency for p in patterns)
            
            insights[pattern_type] = {
                "pattern_count": len(patterns),
                "avg_confidence": avg_confidence,
                "total_frequency": total_frequency,
                "strength": "strong" if avg_confidence > 0.7 else "moderate"
            }
        
        # Log insights for debugging
        self.logger.info(f"🧠 Pattern analysis: {json.dumps(insights, indent=2)}")
    
    async def get_learning_insights(self) -> Dict[str, Any]:
        """Get current learning insights and user profile"""
        return {
            "user_profile": asdict(self.user_profile) if self.user_profile else {},
            "learning_patterns": {
                pid: asdict(pattern) for pid, pattern in self.user_patterns.items()
            },
            "adaptation_cycles": self.adaptation_cycles,
            "improvement_queue_size": len(self.improvement_queue),
            "agent_performance_summary": {
                agent_id: {
                    "total_interactions": len(metrics),
                    "avg_success_rate": sum(m.success_rate for m in metrics) / len(metrics) if metrics else 0,
                    "avg_satisfaction": sum(m.user_satisfaction for m in metrics) / len(metrics) if metrics else 0
                }
                for agent_id, metrics in self.agent_metrics.items()
            }
        }
    
    async def _save_learning_state(self):
        """Save current learning state to databases"""
        try:
            # Save patterns
            patterns_conn = sqlite3.connect(self.patterns_db)
            for pattern in self.user_patterns.values():
                patterns_conn.execute("""
                    INSERT OR REPLACE INTO learning_patterns 
                    (pattern_id, pattern_type, confidence, frequency, last_observed, context, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.pattern_id,
                    pattern.pattern_type,
                    pattern.confidence,
                    pattern.frequency,
                    pattern.last_observed.isoformat(),
                    json.dumps(pattern.context),
                    json.dumps(pattern.metadata)
                ))
            patterns_conn.commit()
            patterns_conn.close()
            
            # Save performance metrics
            performance_conn = sqlite3.connect(self.performance_db)
            for agent_id, metrics in self.agent_metrics.items():
                for metric in metrics[-10:]:  # Save last 10 metrics per agent
                    performance_conn.execute("""
                        INSERT OR REPLACE INTO agent_performance
                        (agent_id, task_type, success_rate, response_time, user_satisfaction, improvement_suggestions, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        metric.agent_id,
                        metric.task_type,
                        metric.success_rate,
                        metric.response_time,
                        metric.user_satisfaction,
                        json.dumps(metric.improvement_suggestions),
                        metric.timestamp.isoformat()
                    ))
            performance_conn.commit()
            performance_conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to save learning state: {e}")
    
    async def _load_learning_history(self):
        """Load previous learning history from databases"""
        try:
            # Load patterns
            if self.patterns_db.exists():
                patterns_conn = sqlite3.connect(self.patterns_db)
                cursor = patterns_conn.execute("SELECT * FROM learning_patterns")
                
                for row in cursor.fetchall():
                    pattern = LearningPattern(
                        pattern_id=row[0],
                        pattern_type=row[1],
                        confidence=row[2],
                        frequency=row[3],
                        last_observed=datetime.fromisoformat(row[4]),
                        context=json.loads(row[5]),
                        metadata=json.loads(row[6])
                    )
                    self.user_patterns[pattern.pattern_id] = pattern
                
                patterns_conn.close()
                self.logger.info(f"Loaded {len(self.user_patterns)} learning patterns")
            
        except Exception as e:
            self.logger.error(f"Failed to load learning history: {e}")


class DigitalTwinEngine:
    """Creates and maintains a digital twin of the user's mind and preferences"""
    
    def __init__(self, evolution_engine: NeuroEvolutionEngine):
        self.evolution_engine = evolution_engine
        self.logger = logging.getLogger("nova.digital_twin")
        
        # Digital twin components
        self.cognitive_model = {}
        self.preference_model = {}
        self.behavioral_model = {}
        self.knowledge_model = {}
    
    async def build_digital_twin(self) -> Dict[str, Any]:
        """Build comprehensive digital twin from learning data"""
        insights = await self.evolution_engine.get_learning_insights()
        
        # Build cognitive model
        self.cognitive_model = await self._build_cognitive_model(insights)
        
        # Build preference model
        self.preference_model = await self._build_preference_model(insights)
        
        # Build behavioral model
        self.behavioral_model = await self._build_behavioral_model(insights)
        
        return {
            "digital_twin": {
                "cognitive_model": self.cognitive_model,
                "preference_model": self.preference_model,
                "behavioral_model": self.behavioral_model,
                "twin_confidence": self._calculate_twin_confidence(),
                "last_updated": datetime.now().isoformat()
            }
        }
    
    async def _build_cognitive_model(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Build model of user's cognitive patterns"""
        user_profile = insights.get("user_profile", {})
        
        return {
            "thinking_style": user_profile.get("communication_style", {}),
            "problem_solving_approach": "analytical",  # Would be learned
            "learning_preferences": {
                "speed": user_profile.get("learning_speed", 1.0),
                "style": "visual"  # Would be detected
            },
            "attention_patterns": user_profile.get("work_patterns", {}),
            "decision_making_style": "deliberate"  # Would be learned
        }
    
    def _calculate_twin_confidence(self) -> float:
        """Calculate confidence in digital twin accuracy"""
        pattern_count = len(self.evolution_engine.user_patterns)
        interaction_count = sum(len(metrics) for metrics in self.evolution_engine.agent_metrics.values())
        
        # Simple confidence calculation
        confidence = min((pattern_count * 0.01 + interaction_count * 0.001), 1.0)
        return round(confidence, 3)
