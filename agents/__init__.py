"""
NOVA Specialized Agents Package

This package contains all specialized agent implementations for NOVA's
multi-agent architecture. Each agent is designed to handle specific
types of tasks and domains.
"""

from .life_manager import LifeManagerAgent
from .finance import FinanceAgent
from .data_analyst import DataAnalystAgent
from .creative import CreativeAgent
from .instructor import AIInstructorAgent

__all__ = [
    'LifeManagerAgent',
    'FinanceAgent', 
    'DataAnalystAgent',
    'CreativeAgent',
    'AIInstructorAgent'
]
