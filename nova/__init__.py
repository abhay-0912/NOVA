"""NOVA - Professional AI Assistant Package"""

__version__ = "2.0.0"
__author__ = "NOVA Team"
__description__ = "Neural Omnipresent Virtual Assistant - Professional AI Assistant"

from .core.assistant import NovaAssistant
from .core.config import NovaConfig

__all__ = ["NovaAssistant", "NovaConfig"]
