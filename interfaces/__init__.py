"""
NOVA Interfaces Module

Contains all user interface components for NOVA including:
- Web API
- CLI interface
- Desktop application
- Mobile app
- Browser extension
"""

from .api import create_nova_api
from .cli import NOVACLIInterface

__all__ = ["create_nova_api", "NOVACLIInterface"]
