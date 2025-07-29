#!/usr/bin/env python3
"""
NOVA - Neural Omnipresent Virtual Assistant
Simple launcher without emoji logging for Windows compatibility
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.brain import NOVABrain, NOVAConfig
from core.memory import MemorySystem
from core.personality import PersonalityEngine
from core.orchestrator import AgentOrchestrator
from core.security import SecurityCore
from interfaces.api import create_nova_api
from interfaces.cli import NOVACLIInterface

class NOVAMain:
    """Main NOVA application coordinator"""
    
    def __init__(self):
        self.config = NOVAConfig()
        # Simple logger setup without emojis
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.brain = None
        self.memory = None
        self.personality = None
        self.orchestrator = None
        self.security = None
        
        # Interfaces
        self.api = None
        self.cli = None
        
        # Runtime state
        self.running = False
        self.tasks = []
        
    async def initialize(self):
        """Initialize all NOVA components"""
        try:
            self.logger.info("Initializing NOVA...")
            
            # Initialize memory system
            self.memory = MemorySystem(self.config.memory)
            await self.memory.initialize()
            
            # Initialize security core
            security_config = getattr(self.config, 'security', {})
            self.security = SecurityCore(security_config)
            await self.security.initialize()
            
            # Initialize personality engine
            self.personality = PersonalityEngine(self.config.personality)
            
            # Initialize brain
            self.brain = NOVABrain(self.config)
            
            # Initialize agent orchestrator
            self.orchestrator = AgentOrchestrator(self.config.agents)
            await self.orchestrator.initialize()
            
            # Initialize interfaces
            self.api = create_nova_api(self.brain, self.config)
            self.cli = NOVACLIInterface(self.brain)
            
            self.logger.info("NOVA initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"NOVA initialization failed: {e}")
            return False
    
    async def run(self):
        """Run NOVA in the selected mode"""
        if not await self.initialize():
            return False
            
        self.running = True
        mode = getattr(self.config.runtime, 'mode', 'cli')
        
        try:
            if mode == 'api':
                self.logger.info("Starting NOVA in API mode...")
                # Start API server
                import uvicorn
                uvicorn.run(
                    self.api,
                    host=self.config.runtime.api_host,
                    port=self.config.runtime.api_port
                )
            elif mode == 'cli':
                self.logger.info("Starting NOVA in CLI mode...")
                await self.cli.start()
            else:
                self.logger.error(f"Unknown mode: {mode}")
                return False
                
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        except Exception as e:
            self.logger.error(f"Runtime error: {e}")
            return False
        finally:
            await self.shutdown()
            
        return True
    
    async def shutdown(self):
        """Gracefully shutdown NOVA"""
        self.logger.info("Shutting down NOVA...")
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Shutdown components
        if self.orchestrator:
            await self.orchestrator.shutdown()
        if self.security:
            await self.security.shutdown()
        if self.memory:
            await self.memory.close()
            
        self.logger.info("NOVA shutdown completed")

async def main():
    """Main entry point"""
    try:
        nova = NOVAMain()
        success = await nova.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        logging.error(f"Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
