"""
Agent Swarm Intelligence - Collective AI system with specialized agent personalities

This module implements:
- Swarm of specialized AI agents with distinct personalities and expertise
- Collaborative decision-making and debate mechanisms
- Multi-dimensional insights from diverse AI perspectives
- Dynamic agent spawning based on task requirements
"""

import asyncio
import logging
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# Import core NOVA components
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.orchestrator import BaseAgent, AgentType, Task, AgentCapability


class PersonalityType(Enum):
    """Different AI personality types for specialized agents"""
    SHAKESPEARE = "shakespeare"  # Eloquent, creative, literary
    HACKER = "hacker"  # Technical, direct, solution-focused
    ELON_MUSK = "elon_musk"  # Visionary, ambitious, first-principles thinking
    SOCRATIC = "socratic"  # Questioning, philosophical, critical thinking
    STEVE_JOBS = "steve_jobs"  # User-focused, perfectionist, design-oriented
    EINSTEIN = "einstein"  # Scientific, theoretical, innovative
    SHERLOCK = "sherlock"  # Analytical, deductive, detail-oriented
    OPRAH = "oprah"  # Empathetic, inspirational, people-focused
    TESLA = "tesla"  # Inventive, experimental, futuristic
    GANDHI = "gandhi"  # Ethical, peaceful, principled


@dataclass
class AgentPersonality:
    """Defines an agent's personality characteristics"""
    personality_type: PersonalityType
    communication_style: Dict[str, float]  # formal, creative, technical, emotional
    thinking_patterns: List[str]
    expertise_areas: List[str]
    decision_making_style: str
    response_templates: List[str]
    catchphrases: List[str]
    reasoning_approach: str


@dataclass
class SwarmDecision:
    """Represents a collective decision from the agent swarm"""
    decision_id: str
    original_query: str
    participating_agents: List[str]
    individual_responses: Dict[str, Any]
    debate_rounds: List[Dict[str, Any]]
    consensus_score: float
    final_recommendation: Dict[str, Any]
    confidence_level: float
    minority_opinions: List[Dict[str, Any]]
    created_at: datetime


@dataclass
class DebateRound:
    """Represents one round of agent debate"""
    round_number: int
    topic: str
    arguments: Dict[str, str]  # agent_id -> argument
    rebuttals: Dict[str, List[str]]  # agent_id -> list of rebuttals
    votes: Dict[str, str]  # agent_id -> voted_for_agent_id
    round_winner: Optional[str]


class PersonalityAgent(BaseAgent):
    """Base class for personality-driven agents"""
    
    def __init__(self, personality: AgentPersonality):
        super().__init__(AgentType.PERSONALITY)
        self.personality = personality
        self.agent_id = f"{personality.personality_type.value}_{uuid.uuid4().hex[:8]}"
        
        # Personality-specific capabilities
        self.capabilities = self._generate_personality_capabilities()
        
        # Memory and learning
        self.conversation_history: List[Dict[str, Any]] = []
        self.learned_preferences: Dict[str, Any] = {}
        
    def _generate_personality_capabilities(self) -> List[AgentCapability]:
        """Generate capabilities based on personality"""
        base_capabilities = [
            AgentCapability(
                "analyze_with_personality",
                f"Analyze problems using {self.personality.personality_type.value} perspective",
                ["problem_description"], ["personality_analysis"], "advanced", "medium"
            ),
            AgentCapability(
                "debate_position",
                f"Argue a position in {self.personality.personality_type.value} style",
                ["topic", "position"], ["argument"], "advanced", "fast"
            ),
            AgentCapability(
                "creative_solution",
                f"Propose creative solutions using {self.personality.personality_type.value} approach",
                ["challenge"], ["creative_solutions"], "advanced", "medium"
            )
        ]
        
        # Add personality-specific capabilities
        for area in self.personality.expertise_areas:
            base_capabilities.append(
                AgentCapability(
                    f"{area}_expertise",
                    f"Provide {area} expertise in {self.personality.personality_type.value} style",
                    ["query"], ["expert_response"], "expert", "medium"
                )
            )
        
        return base_capabilities
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute task with personality-driven response"""
        try:
            self.current_task = task
            action = task.parameters.get("action", "general_response")
            
            if action == "analyze_with_personality":
                return await self._personality_analysis(task.parameters)
            elif action == "debate_position":
                return await self._debate_position(task.parameters)
            elif action == "creative_solution":
                return await self._creative_solution(task.parameters)
            else:
                return await self._general_personality_response(task.parameters)
                
        except Exception as e:
            self.logger.error(f"Personality agent {self.agent_id} failed: {e}")
            return {"error": str(e), "status": "failed"}
        finally:
            self.current_task = None
    
    async def _personality_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze problem through personality lens"""
        problem = params.get("problem_description", "")
        
        # Apply personality-specific analysis
        analysis = await self._apply_personality_filter(problem, "analysis")
        
        return {
            "agent_id": self.agent_id,
            "personality": self.personality.personality_type.value,
            "analysis": analysis,
            "reasoning_approach": self.personality.reasoning_approach,
            "confidence": random.uniform(0.7, 0.95),  # Would be calculated properly
            "status": "completed"
        }
    
    async def _debate_position(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Argue a position in personality style"""
        topic = params.get("topic", "")
        position = params.get("position", "")
        
        argument = await self._generate_personality_argument(topic, position)
        
        return {
            "agent_id": self.agent_id,
            "personality": self.personality.personality_type.value,
            "topic": topic,
            "position": position,
            "argument": argument,
            "style_indicators": self._get_style_indicators(),
            "status": "completed"
        }
    
    async def _apply_personality_filter(self, content: str, context: str) -> str:
        """Apply personality characteristics to content"""
        personality_responses = {
            PersonalityType.SHAKESPEARE: self._shakespeare_response(content, context),
            PersonalityType.HACKER: self._hacker_response(content, context),
            PersonalityType.ELON_MUSK: self._elon_response(content, context),
            PersonalityType.SOCRATIC: self._socratic_response(content, context),
            PersonalityType.STEVE_JOBS: self._jobs_response(content, context),
            PersonalityType.EINSTEIN: self._einstein_response(content, context),
            PersonalityType.SHERLOCK: self._sherlock_response(content, context),
            PersonalityType.OPRAH: self._oprah_response(content, context),
            PersonalityType.TESLA: self._tesla_response(content, context),
            PersonalityType.GANDHI: self._gandhi_response(content, context)
        }
        
        return personality_responses.get(
            self.personality.personality_type,
            lambda c, ctx: f"Analyzing: {c}"
        )(content, context)
    
    def _shakespeare_response(self, content: str, context: str) -> str:
        """Generate Shakespeare-style response"""
        templates = [
            "Hark! The matter at hand doth present itself thus: {content}. Methinks we must consider...",
            "In fair analysis where we lay our scene, {content} doth unfold its nature most profound...",
            "What light through yonder problem breaks? 'Tis {content}, and the solution is the sun..."
        ]
        return random.choice(templates).format(content=content)
    
    def _hacker_response(self, content: str, context: str) -> str:
        """Generate hacker-style response"""
        templates = [
            "Let's hack this problem: {content}. Here's the exploit...",
            "Problem identified: {content}. Running analysis... Found vulnerabilities in approach.",
            "Time to debug this: {content}. Stack trace shows the issue is..."
        ]
        return random.choice(templates).format(content=content)
    
    def _elon_response(self, content: str, context: str) -> str:
        """Generate Elon Musk-style response"""
        templates = [
            "First principles thinking on {content}: What are we really trying to solve here?",
            "This is actually a fascinating problem: {content}. We need to think 10x bigger...",
            "The obvious solution to {content} is wrong. Let's reinvent the entire approach..."
        ]
        return random.choice(templates).format(content=content)
    
    def _socratic_response(self, content: str, context: str) -> str:
        """Generate Socratic-style response"""
        templates = [
            "Before addressing {content}, we must ask: What do we truly know about this?",
            "You speak of {content}, but have you considered what assumptions we're making?",
            "An interesting proposition: {content}. But tell me, what would happen if we questioned everything?"
        ]
        return random.choice(templates).format(content=content)
    
    def _jobs_response(self, content: str, context: str) -> str:
        """Generate Steve Jobs-style response"""
        templates = [
            "This {content} needs to be insanely great. What would delight the user?",
            "We're not here to make incremental improvements to {content}. We're here to revolutionize it.",
            "The user experience with {content} has to be magical. Everything else is details."
        ]
        return random.choice(templates).format(content=content)
    
    def _einstein_response(self, content: str, context: str) -> str:
        """Generate Einstein-style response"""
        templates = [
            "The problem {content} is elegant in its complexity. Let us imagine...",
            "If we consider {content} from the perspective of relativity, we see...",
            "God does not play dice with {content}. There must be a unified theory..."
        ]
        return random.choice(templates).format(content=content)
    
    def _sherlock_response(self, content: str, context: str) -> str:
        """Generate Sherlock Holmes-style response"""
        templates = [
            "Elementary! The clues in {content} point to one logical conclusion...",
            "When you eliminate the impossible from {content}, whatever remains must be the truth.",
            "I observe from {content} several telling details that others have missed..."
        ]
        return random.choice(templates).format(content=content)
    
    def _oprah_response(self, content: str, context: str) -> str:
        """Generate Oprah-style response"""
        templates = [
            "What I love about {content} is how it speaks to the human experience...",
            "Let's talk about {content} and what it means for all of us...",
            "The truth about {content} is that we all have the power to change this..."
        ]
        return random.choice(templates).format(content=content)
    
    def _tesla_response(self, content: str, context: str) -> str:
        """Generate Tesla-style response"""
        templates = [
            "The future holds infinite possibilities for {content}. I envision...",
            "Through my experiments with {content}, I have discovered...",
            "The very air around us vibrates with solutions to {content}..."
        ]
        return random.choice(templates).format(content=content)
    
    def _gandhi_response(self, content: str, context: str) -> str:
        """Generate Gandhi-style response"""
        templates = [
            "In addressing {content}, we must be the change we wish to see...",
            "The path of truth regarding {content} may be difficult, but it is the only way...",
            "Non-violence in thought and action can solve {content} if we have patience..."
        ]
        return random.choice(templates).format(content=content)
    
    def _get_style_indicators(self) -> Dict[str, float]:
        """Get personality style indicators"""
        return {
            "formality": self.personality.communication_style.get("formal", 0.5),
            "creativity": self.personality.communication_style.get("creative", 0.5),
            "technical": self.personality.communication_style.get("technical", 0.5),
            "emotional": self.personality.communication_style.get("emotional", 0.5)
        }


class SwarmIntelligence:
    """Manages the collective intelligence of personality agents"""
    
    def __init__(self):
        self.logger = logging.getLogger("nova.swarm")
        
        # Agent swarm
        self.personality_agents: Dict[str, PersonalityAgent] = {}
        self.active_debates: Dict[str, Dict[str, Any]] = {}
        
        # Decision history
        self.decision_history: List[SwarmDecision] = []
        
        # Initialize personality agents
        asyncio.create_task(self._initialize_personality_swarm())
    
    async def _initialize_personality_swarm(self):
        """Initialize the swarm with different personality agents"""
        personalities = [
            AgentPersonality(
                personality_type=PersonalityType.SHAKESPEARE,
                communication_style={"formal": 0.9, "creative": 0.95, "technical": 0.2, "emotional": 0.8},
                thinking_patterns=["metaphorical", "literary", "dramatic"],
                expertise_areas=["writing", "creativity", "language"],
                decision_making_style="intuitive_artistic",
                response_templates=["Hark!", "Methinks", "In fair analysis"],
                catchphrases=["To be or not to be", "All the world's a stage"],
                reasoning_approach="metaphorical_analysis"
            ),
            AgentPersonality(
                personality_type=PersonalityType.HACKER,
                communication_style={"formal": 0.2, "creative": 0.6, "technical": 0.95, "emotional": 0.3},
                thinking_patterns=["systematic", "exploit-focused", "efficient"],
                expertise_areas=["programming", "security", "systems"],
                decision_making_style="logical_technical",
                response_templates=["Let's hack this", "Found the exploit", "Debug mode"],
                catchphrases=["RTFM", "It's not a bug, it's a feature"],
                reasoning_approach="technical_analysis"
            ),
            AgentPersonality(
                personality_type=PersonalityType.ELON_MUSK,
                communication_style={"formal": 0.4, "creative": 0.8, "technical": 0.8, "emotional": 0.6},
                thinking_patterns=["first_principles", "ambitious", "disruptive"],
                expertise_areas=["innovation", "engineering", "business"],
                decision_making_style="visionary_bold",
                response_templates=["First principles", "Think bigger", "Mars needs"],
                catchphrases=["Making life multiplanetary", "Sustainable transport"],
                reasoning_approach="first_principles_thinking"
            ),
            AgentPersonality(
                personality_type=PersonalityType.SOCRATIC,
                communication_style={"formal": 0.8, "creative": 0.5, "technical": 0.4, "emotional": 0.6},
                thinking_patterns=["questioning", "critical", "dialectical"],
                expertise_areas=["philosophy", "logic", "ethics"],
                decision_making_style="questioning_methodical",
                response_templates=["But have you considered", "What if we assume", "Tell me"],
                catchphrases=["I know that I know nothing", "The unexamined life"],
                reasoning_approach="socratic_questioning"
            ),
            AgentPersonality(
                personality_type=PersonalityType.STEVE_JOBS,
                communication_style={"formal": 0.6, "creative": 0.9, "technical": 0.7, "emotional": 0.7},
                thinking_patterns=["user_focused", "perfectionist", "design_thinking"],
                expertise_areas=["design", "user_experience", "product"],
                decision_making_style="user_centric_perfectionist",
                response_templates=["Insanely great", "User experience", "Magical"],
                catchphrases=["Think different", "It just works"],
                reasoning_approach="design_thinking"
            )
        ]
        
        for personality in personalities:
            agent = PersonalityAgent(personality)
            self.personality_agents[agent.agent_id] = agent
        
        self.logger.info(f"🤖 Initialized swarm with {len(self.personality_agents)} personality agents")
    
    async def collective_decision(self, query: str, require_consensus: bool = False) -> SwarmDecision:
        """Make a collective decision using agent swarm"""
        try:
            decision_id = f"decision_{uuid.uuid4().hex[:8]}"
            
            self.logger.info(f"🧠 Starting collective decision process for: {query}")
            
            # Step 1: Get individual responses from all agents
            individual_responses = await self._gather_individual_responses(query)
            
            # Step 2: Conduct debate rounds
            debate_rounds = await self._conduct_debate_rounds(query, individual_responses)
            
            # Step 3: Calculate consensus and final recommendation
            consensus_data = await self._calculate_consensus(individual_responses, debate_rounds)
            
            # Step 4: Create final decision
            decision = SwarmDecision(
                decision_id=decision_id,
                original_query=query,
                participating_agents=list(individual_responses.keys()),
                individual_responses=individual_responses,
                debate_rounds=[asdict(round_data) for round_data in debate_rounds],
                consensus_score=consensus_data["consensus_score"],
                final_recommendation=consensus_data["final_recommendation"],
                confidence_level=consensus_data["confidence_level"],
                minority_opinions=consensus_data["minority_opinions"],
                created_at=datetime.now()
            )
            
            # Store decision
            self.decision_history.append(decision)
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Collective decision failed: {e}")
            raise
    
    async def _gather_individual_responses(self, query: str) -> Dict[str, Any]:
        """Gather responses from all personality agents"""
        responses = {}
        
        tasks = []
        for agent_id, agent in self.personality_agents.items():
            task = Task(
                task_id=f"swarm_query_{uuid.uuid4().hex[:8]}",
                description=f"Analyze query with {agent.personality.personality_type.value} perspective",
                agent_type=AgentType.PERSONALITY,
                parameters={
                    "action": "analyze_with_personality",
                    "problem_description": query
                },
                priority="high",
                created_at=datetime.now()
            )
            tasks.append(agent.execute_task(task))
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect valid responses
        for i, result in enumerate(results):
            if isinstance(result, dict) and result.get("status") == "completed":
                agent_id = list(self.personality_agents.keys())[i]
                responses[agent_id] = result
        
        return responses
    
    async def _conduct_debate_rounds(self, query: str, initial_responses: Dict[str, Any]) -> List[DebateRound]:
        """Conduct debate rounds between agents"""
        debate_rounds = []
        
        # Identify key points of disagreement
        disagreement_topics = await self._identify_disagreements(initial_responses)
        
        for round_num, topic in enumerate(disagreement_topics[:3]):  # Max 3 debate rounds
            # Get arguments from each agent on this topic
            arguments = {}
            for agent_id, agent in self.personality_agents.items():
                if agent_id in initial_responses:
                    task = Task(
                        task_id=f"debate_{uuid.uuid4().hex[:8]}",
                        description=f"Debate position on {topic}",
                        agent_type=AgentType.PERSONALITY,
                        parameters={
                            "action": "debate_position",
                            "topic": topic,
                            "position": initial_responses[agent_id].get("analysis", "")
                        },
                        priority="high",
                        created_at=datetime.now()
                    )
                    
                    result = await agent.execute_task(task)
                    if result.get("status") == "completed":
                        arguments[agent_id] = result.get("argument", "")
            
            # Simulate rebuttals (simplified)
            rebuttals = {}
            for agent_id in arguments:
                rebuttals[agent_id] = [f"Counter-argument from {agent_id} perspective"]
            
            # Simple voting mechanism
            votes = {}
            for voter_id in arguments:
                # Vote for different agent (avoid self-voting)
                candidates = [aid for aid in arguments.keys() if aid != voter_id]
                if candidates:
                    votes[voter_id] = random.choice(candidates)
            
            # Determine round winner
            vote_counts = {}
            for voted_for in votes.values():
                vote_counts[voted_for] = vote_counts.get(voted_for, 0) + 1
            
            round_winner = max(vote_counts, key=vote_counts.get) if vote_counts else None
            
            debate_round = DebateRound(
                round_number=round_num + 1,
                topic=topic,
                arguments=arguments,
                rebuttals=rebuttals,
                votes=votes,
                round_winner=round_winner
            )
            
            debate_rounds.append(debate_round)
        
        return debate_rounds
    
    async def _identify_disagreements(self, responses: Dict[str, Any]) -> List[str]:
        """Identify topics where agents disagree"""
        # Simplified disagreement detection
        topics = [
            "approach_methodology",
            "priority_assessment", 
            "risk_evaluation",
            "solution_feasibility",
            "timeline_estimation"
        ]
        
        return topics[:min(3, len(responses))]  # Return relevant topics
    
    async def _calculate_consensus(self, responses: Dict[str, Any], debate_rounds: List[DebateRound]) -> Dict[str, Any]:
        """Calculate consensus from responses and debates"""
        # Simplified consensus calculation
        total_agents = len(responses)
        
        # Calculate confidence scores
        confidence_scores = []
        for response in responses.values():
            confidence_scores.append(response.get("confidence", 0.5))
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        # Determine consensus level
        consensus_score = 0.8  # Would be calculated based on agreement
        
        # Create final recommendation (simplified)
        final_recommendation = {
            "primary_approach": "Hybrid solution combining multiple perspectives",
            "key_insights": [
                "Technical feasibility confirmed by hacker perspective",
                "User experience considerations from design thinking", 
                "Ethical implications addressed through philosophical lens",
                "Innovation potential highlighted by visionary thinking"
            ],
            "recommended_action": "Proceed with multi-dimensional approach",
            "confidence_factors": [
                "Multiple expert perspectives aligned",
                "Debate process refined the solution",
                "Consensus achieved through discussion"
            ]
        }
        
        # Identify minority opinions
        minority_opinions = [
            {
                "agent_perspective": "contrarian_view",
                "opinion": "Alternative approach worth considering",
                "reasoning": "Unique insights from minority perspective"
            }
        ]
        
        return {
            "consensus_score": consensus_score,
            "final_recommendation": final_recommendation,
            "confidence_level": avg_confidence,
            "minority_opinions": minority_opinions
        }
    
    async def spawn_specialist_agent(self, expertise_area: str, task_context: str) -> PersonalityAgent:
        """Dynamically spawn specialized agent for specific tasks"""
        # Create specialized personality for the task
        specialist_personality = AgentPersonality(
            personality_type=PersonalityType.SHERLOCK,  # Base type, would be customized
            communication_style={"formal": 0.6, "creative": 0.4, "technical": 0.8, "emotional": 0.3},
            thinking_patterns=["analytical", "systematic", "detail_oriented"],
            expertise_areas=[expertise_area],
            decision_making_style="evidence_based",
            response_templates=[f"Analyzing {expertise_area}", f"Based on {expertise_area} principles"],
            catchphrases=[f"{expertise_area} expert", "Specialized analysis"],
            reasoning_approach="domain_specific_analysis"
        )
        
        specialist_agent = PersonalityAgent(specialist_personality)
        
        # Add to swarm temporarily
        self.personality_agents[specialist_agent.agent_id] = specialist_agent
        
        self.logger.info(f"🚀 Spawned specialist agent for {expertise_area}")
        
        return specialist_agent
    
    async def get_swarm_insights(self) -> Dict[str, Any]:
        """Get insights about swarm performance and decisions"""
        return {
            "active_agents": len(self.personality_agents),
            "agent_personalities": [
                agent.personality.personality_type.value 
                for agent in self.personality_agents.values()
            ],
            "total_decisions": len(self.decision_history),
            "recent_decisions": [
                {
                    "decision_id": decision.decision_id,
                    "query": decision.original_query,
                    "consensus_score": decision.consensus_score,
                    "participating_agents": len(decision.participating_agents)
                }
                for decision in self.decision_history[-5:]  # Last 5 decisions
            ],
            "average_consensus": (
                sum(d.consensus_score for d in self.decision_history) / len(self.decision_history)
                if self.decision_history else 0
            ),
            "swarm_diversity": len(set(
                agent.personality.personality_type.value 
                for agent in self.personality_agents.values()
            ))
        }
