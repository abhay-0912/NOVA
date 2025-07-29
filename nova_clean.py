#!/usr/bin/env python3
"""
NOVA - Neural Omnipresent Virtual Assistant
Professional AI Assistant with Multi-Model Support

A clean, professional implementation focusing on:
- Reliable AI responses with fallback systems
- Simple, maintainable code architecture  
- Professional error handling and logging
- Multi-provider AI integration (Gemini, OpenAI, Anthropic)
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from nova.core.config import NovaConfig
from nova.core.logger import setup_logging
from nova.core.assistant import NovaAssistant
from nova.cli.interface import CliInterface


class Nova:
    """Main NOVA application class."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize NOVA with configuration."""
        self.config = NovaConfig.load(config_path)
        self.logger = setup_logging(self.config.log_level)
        self.assistant = NovaAssistant(self.config)
        self.cli = CliInterface(self.assistant)
        
    async def start(self):
        """Start NOVA in interactive mode."""
        try:
            self.logger.info("🚀 Starting NOVA - Neural Omnipresent Virtual Assistant")
            await self.assistant.initialize()
            await self.cli.start()
        except KeyboardInterrupt:
            self.logger.info("👋 NOVA shutdown requested by user")
        except Exception as e:
            self.logger.error(f"❌ NOVA startup failed: {e}")
            raise
        finally:
            await self.assistant.shutdown()
            
    async def process_single_query(self, query: str) -> str:
        """Process a single query and return the response."""
        await self.assistant.initialize()
        try:
            response = await self.assistant.process_query(query)
            return response.content
        finally:
            await self.assistant.shutdown()


def main():
    """Main entry point for NOVA."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="NOVA - Neural Omnipresent Virtual Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start interactive mode
  %(prog)s -q "Hello NOVA"    # Process single query
  %(prog)s --config custom.env # Use custom config
        """
    )
    
    parser.add_argument(
        "-q", "--query",
        help="Process a single query and exit"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file (default: .env)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set up basic logging for startup
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    nova = Nova(args.config)
    
    try:
        if args.query:
            # Single query mode
            response = asyncio.run(nova.process_single_query(args.query))
            print(response)
        else:
            # Interactive mode
            asyncio.run(nova.start())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
