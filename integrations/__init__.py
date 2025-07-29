"""
NOVA Integrations Package

This package contains integrations with external services and APIs
to extend NOVA's capabilities and connect with third-party platforms.
"""

from .github_integration import GitHubIntegration
from .email_integration import EmailIntegration
from .calendar_integration import CalendarIntegration
from .slack_integration import SlackIntegration

__all__ = [
    'GitHubIntegration',
    'EmailIntegration', 
    'CalendarIntegration',
    'SlackIntegration'
]
