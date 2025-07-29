"""
NOVA Brain - The central intelligence system

This is the main brain that coordinates all of NOVA's capabilities,
from multi-agent orchestration to decision making.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .memory import MemorySystem
from .personality import PersonalityEngine
from .orchestrator import AgentOrchestrator


class NOVAState(Enum):
    """NOVA operational states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    LEARNING = "learning"
    SLEEPING = "sleeping"
    EMERGENCY = "emergency"


@dataclass
class NOVAConfig:
    """NOVA configuration settings"""
    name: str = "NOVA"
    personality: str = "assistant"
    voice_enabled: bool = True
    vision_enabled: bool = True
    security_level: str = "high"
    local_mode: bool = True
    cloud_fallback: bool = True
    learning_enabled: bool = True
    debug_mode: bool = False


class NOVABrain:
    """
    The central brain of NOVA that orchestrates all capabilities
    """
    
    def __init__(self, config: NOVAConfig):
        self.config = config
        self.state = NOVAState.INITIALIZING
        self.logger = self._setup_logging()
        
        # Core systems
        self.memory = MemorySystem()
        self.personality = PersonalityEngine(config.personality)
        self.orchestrator = AgentOrchestrator()
        
        # Capabilities flags
        self.capabilities = {
            "voice": config.voice_enabled,
            "vision": config.vision_enabled,
            "automation": True,
            "security": True,
            "learning": config.learning_enabled
        }
        
        self.logger.info(f"NOVA Brain initialized with config: {config}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for NOVA"""
        logger = logging.getLogger("nova.brain")
        logger.setLevel(logging.DEBUG if self.config.debug_mode else logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - NOVA.%(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self) -> bool:
        """Initialize all NOVA systems"""
        try:
            self.logger.info("🧠 Initializing NOVA Brain...")
            
            # Initialize core systems
            await self.memory.initialize()
            await self.personality.initialize()
            await self.orchestrator.initialize()
            
            self.state = NOVAState.ACTIVE
            self.logger.info("✅ NOVA Brain initialization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ NOVA Brain initialization failed: {e}")
            self.state = NOVAState.EMERGENCY
            return False
    
    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user input through NOVA's intelligence pipeline
        
        Args:
            input_data: Dictionary containing input type, content, and metadata
            
        Returns:
            Dictionary containing NOVA's response and actions
        """
        try:
            input_type = input_data.get("type", "text")
            content = input_data.get("content", "")
            context = input_data.get("context", {})
            
            self.logger.info(f"Processing {input_type} input: {content[:100]}...")
            
            # Store input in memory
            await self.memory.store_interaction(input_data)
            
            # Get personality-adjusted response style
            response_style = self.personality.get_response_style(context)
            
            # Route to appropriate agent(s)
            response = await self.orchestrator.process_request(
                input_data, response_style
            )
            
            # Learn from interaction
            if self.capabilities["learning"]:
                await self._learn_from_interaction(input_data, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return {
                "error": "Sorry, I encountered an issue processing your request.",
                "type": "error"
            }
    
    async def _learn_from_interaction(self, input_data: Dict[str, Any], response: Dict[str, Any]):
        """Learn and adapt from user interactions"""
        try:
            # Update personality based on user feedback
            if input_data.get("feedback"):
                await self.personality.update_from_feedback(input_data["feedback"])
            
            # Store successful patterns in memory
            await self.memory.store_pattern(input_data, response)
            
        except Exception as e:
            self.logger.error(f"Learning error: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current NOVA status and health"""
        return {
            "state": self.state.value,
            "capabilities": self.capabilities,
            "memory_stats": await self.memory.get_stats(),
            "active_agents": await self.orchestrator.get_active_agents(),
            "personality": self.personality.current_personality
        }
    
    async def shutdown(self):
        """Gracefully shutdown NOVA"""
        self.logger.info("🔄 Shutting down NOVA Brain...")
        
        await self.orchestrator.shutdown()
        await self.memory.cleanup()
        
        self.state = NOVAState.SLEEPING
        self.logger.info("😴 NOVA Brain shutdown complete")
    
    def set_emergency_mode(self, reason: str):
        """Set NOVA to emergency mode"""
        self.state = NOVAState.EMERGENCY
        self.logger.critical(f"🚨 EMERGENCY MODE ACTIVATED: {reason}")
        
        # Disable non-essential capabilities
        self.capabilities.update({
            "automation": False,
            "learning": False
        })
    
    async def god_mode(self, instruction: str) -> Dict[str, Any]:
        """
        God Mode: Execute complex multi-step instructions
        
        Example: "Plan my next week, find 3 companies to apply to, 
                 rewrite my resume for them, email HRs, and learn DSA 1 hour a day."
        """
        self.logger.info(f"🚀 GOD MODE ACTIVATED: {instruction}")
        
        try:
            # Parse complex instruction into sub-tasks
            tasks = await self.orchestrator.parse_god_mode_instruction(instruction)
            
            # Execute tasks with full automation
            results = []
            for task in tasks:
                result = await self.orchestrator.execute_autonomous_task(task)
                results.append(result)
            
            return {
                "status": "god_mode_complete",
                "instruction": instruction,
                "tasks_executed": len(tasks),
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"God mode error: {e}")
            return {
                "error": "God mode execution failed",
                "instruction": instruction
            }
