"""
Professional CLI Interface for NOVA

Clean, user-friendly command-line interface with proper error handling,
helpful prompts, and professional formatting.
"""

import asyncio
import sys
from typing import Optional, List
from datetime import datetime

from ..core.assistant import NovaAssistant
from ..core.logger import get_logger
from ..ai.client import AIResponse


class CliInterface:
    """Professional command-line interface for NOVA."""
    
    def __init__(self, assistant: NovaAssistant):
        self.assistant = assistant
        self.logger = get_logger("cli")
        self.running = False
        
    async def start(self):
        """Start the interactive CLI."""
        self.running = True
        
        # Display welcome message
        self._show_welcome()
        
        try:
            while self.running:
                try:
                    # Get user input
                    user_input = await self._get_user_input()
                    
                    if not user_input.strip():
                        continue
                    
                    # Handle special commands
                    if self._handle_special_commands(user_input):
                        continue
                    
                    # Process query
                    await self._process_user_query(user_input)
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except EOFError:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    self.logger.error(f"CLI error: {e}")
                    print(f"❌ An error occurred: {e}")
                    
        finally:
            self.running = False
    
    async def _get_user_input(self) -> str:
        """Get input from user with proper prompt."""
        try:
            # Run input in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, 
                input, 
                f"\n🤖 {self.assistant.config.name} > "
            )
        except (KeyboardInterrupt, EOFError):
            raise
        except Exception as e:
            self.logger.error(f"Input error: {e}")
            return ""
    
    async def _process_user_query(self, query: str):
        """Process user query and display response."""
        print("🤔 Thinking...")
        
        try:
            # Process query
            response = await self.assistant.process_query(query)
            
            # Display response
            self._display_response(response)
            
        except Exception as e:
            self.logger.error(f"Query processing error: {e}")
            print(f"❌ Sorry, I encountered an error: {e}")
    
    def _handle_special_commands(self, user_input: str) -> bool:
        """Handle special CLI commands. Returns True if command was handled."""
        command = user_input.strip().lower()
        
        if command in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            self.running = False
            return True
        
        elif command in ['help', '?']:
            self._show_help()
            return True
        
        elif command in ['clear', 'cls']:
            self._clear_screen()
            return True
        
        elif command in ['history', 'h']:
            self._show_history()
            return True
        
        elif command in ['status', 'info']:
            self._show_status()
            return True
        
        elif command in ['clear history', 'clear_history']:
            self.assistant.clear_history()
            print("🗑️ Conversation history cleared")
            return True
        
        return False
    
    def _display_response(self, response: AIResponse):
        """Display AI response with proper formatting."""
        print()
        print("─" * 60)
        print(f"📝 {response.content}")
        print("─" * 60)
        
        # Show metadata in debug mode
        if self.assistant.config.debug:
            metadata = []
            metadata.append(f"Provider: {response.provider}")
            metadata.append(f"Model: {response.model}")
            if response.tokens_used:
                metadata.append(f"Tokens: {response.tokens_used}")
            if response.confidence:
                metadata.append(f"Confidence: {response.confidence:.2f}")
            
            print(f"🔍 Debug: {' | '.join(metadata)}")
    
    def _show_welcome(self):
        """Display welcome message."""
        config = self.assistant.config
        
        print(f"""
╭─────────────────────────────────────────╮
│  🤖 {config.name} - AI Assistant                  │
│  Version {config.version}                         │
│                                         │
│  Type your questions or 'help' for     │
│  available commands.                    │
╰─────────────────────────────────────────╯
        """)
        
        # Show configuration info
        if config.debug:
            print(f"🐛 Debug mode: {config.environment}")
        
        # Show available AI providers
        providers = []
        if config.gemini_api_key:
            providers.append("Gemini")
        if config.openai_api_key:
            providers.append("OpenAI")
        if config.anthropic_api_key:
            providers.append("Anthropic")
        
        if providers:
            print(f"🔑 AI Providers: {', '.join(providers)}")
        else:
            print("⚠️  No AI providers configured - using local responses")
        
        print()
    
    def _show_help(self):
        """Display help information."""
        print("""
📖 Available Commands:
  
  General:
  • help, ?           - Show this help message
  • quit, exit, q     - Exit NOVA
  • clear, cls        - Clear screen
  • status, info      - Show system status
  
  Conversation:
  • history, h        - Show conversation history
  • clear history     - Clear conversation history
  
  Examples:
  • "What is artificial intelligence?"
  • "Calculate 15 * 24"
  • "Write a short poem"
  • "Explain quantum computing"
        """)
    
    def _clear_screen(self):
        """Clear the terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        self._show_welcome()
    
    def _show_history(self):
        """Display conversation history."""
        history = self.assistant.conversation_history
        
        if not history:
            print("📝 No conversation history yet")
            return
        
        print("\n📚 Conversation History:")
        print("─" * 50)
        
        for i, entry in enumerate(history[-5:], 1):  # Show last 5 entries
            timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%H:%M:%S")
            print(f"{i}. [{timestamp}] User: {entry['query'][:50]}...")
            print(f"   Assistant: {entry['response'][:50]}...")
            print()
    
    def _show_status(self):
        """Display system status."""
        config = self.assistant.config
        summary = self.assistant.get_conversation_summary()
        
        print(f"""
🔧 System Status:
  • Name: {config.name} v{config.version}
  • Environment: {config.environment}
  • Default AI: {config.default_ai_model}
  • Debug Mode: {'Yes' if config.debug else 'No'}

💬 Conversation:
  • Total Messages: {summary.get('total_exchanges', 0)}
  • Providers Used: {', '.join(summary.get('providers_used', ['None']))}
        """)


# Convenience function for running CLI
async def run_cli(config_path: Optional[str] = None):
    """Run NOVA CLI with optional config path."""
    from ..core.config import NovaConfig
    from ..core.assistant import NovaAssistant
    
    config = NovaConfig.load(config_path)
    assistant = NovaAssistant(config)
    cli = CliInterface(assistant)
    
    try:
        await assistant.initialize()
        await cli.start()
    finally:
        await assistant.shutdown()
