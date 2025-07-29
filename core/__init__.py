"""
NOVA Core Module
Neural Omnipresent Virtual Assistant

This module contains the core engine that orchestrates all NOVA's capabilities.
"""

from .brain import NOVABrain
from .orchestrator import AgentOrchestrator
from .memory import MemorySystem
from .personality import PersonalityEngine
from .security import SecurityCore

__version__ = "0.1.0"
__all__ = [
    "NOVABrain",
    "AgentOrchestrator", 
    "MemorySystem",
    "PersonalityEngine",
    "SecurityCore"
]
