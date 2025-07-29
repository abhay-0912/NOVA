"""
NOVA Main Entry Point - Next-Generation Hyper-Intelligent Ecosystem
Neural Omnipresent Virtual Assistant

Multi-mode deployment supporting:
- CLI: Interactive command-line interface  
- API: Web API server only
- Web: Combined web interface and API
- Daemon: Background service mode
- God: Full hyper-intelligent capabilities (Neural Evolution, Swarm Intelligence, etc.)
"""

import asyncio
import argparse
import sys
import logging
import signal
import uvicorn
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config import config
from core.brain import NOVABrain, NOVAConfig
from core.security import SecurityCore, SecurityConfig
from interfaces.api import create_nova_api
from interfaces.cli import NOVACLIInterface


class NOVAMain:
    """Main NOVA application coordinator with multi-mode support"""
    
    def __init__(self, mode: str = "cli"):
        # Setup logging from configuration
        self._setup_logging()
        self.logger = logging.getLogger("nova.main")
        
        # Create necessary directories
        config.create_dirs()
        
        # Initialize NOVA configuration from config manager
        self.config = NOVAConfig(
            name=config.get('nova.name', 'NOVA'),
            personality=config.get('nova.personality', 'assistant'),
            voice_enabled=config.get('capabilities.voice_enabled', True),
            vision_enabled=config.get('capabilities.vision_enabled', True),
            security_level=config.get('security.security_level', 'high'),
            debug_mode=config.get('nova.debug_mode', False)
        )
        
        self.mode = mode
        
        # Core components
        self.brain = None
        self.security = None
        
        # Interfaces
        self.api = None
        self.cli = None
        
        # Runtime state
        self.running = False
        self.shutdown_event = asyncio.Event()
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_logging(self):
        """Setup application logging from configuration"""
        log_level = getattr(logging, config.get('logging.level', 'INFO'))
        log_format = config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        handlers = []
        
        if config.get('logging.console_enabled', True):
            handlers.append(logging.StreamHandler(sys.stdout))
        
        if config.get('logging.file_enabled', True):
            log_file = Path(config.get('storage.logs_dir', './logs')) / 'nova.log'
            log_file.parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(log_file))
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=handlers
        )
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize(self) -> bool:
        """Initialize all NOVA components"""
        try:
            self.logger.info("Initializing NOVA...")
            
            # Initialize security core first
            security_config = SecurityConfig(
                real_time_monitoring=config.get('security.real_time_monitoring', True),
                auto_threat_response=config.get('security.auto_threat_response', True),
                data_encryption=config.get('security.data_encryption', True)
            )
            self.security = SecurityCore(security_config)
            await self.security.initialize()
            
            # Initialize NOVA brain
            self.brain = NOVABrain(self.config)
            await self.brain.initialize()
            
            # Initialize interfaces based on mode
            if self.mode in ["api", "web", "daemon"]:
                self.api = create_nova_api(self.brain, self.config)
                self.logger.info("API interface initialized")
            
            if self.mode in ["cli", "web"]:
                self.cli = NOVACLIInterface(self.brain)
                self.logger.info("CLI interface initialized")
            
            self.logger.info("NOVA initialization complete!")
            return True
            
        except Exception as e:
            self.logger.error(f"NOVA initialization failed: {e}")
            return False
    
    async def run(self) -> bool:
        """Run NOVA in the specified mode"""
        if not await self.initialize():
            return False
        
        self.running = True
        self.logger.info(f"Starting NOVA in {self.mode} mode...")
        
        try:
            if self.mode == "cli":
                await self._run_cli_mode()
            elif self.mode == "api":
                await self._run_api_mode()
            elif self.mode == "web":
                await self._run_web_mode()
            elif self.mode == "daemon":
                await self._run_daemon_mode()
            else:
                self.logger.error(f"Unknown mode: {self.mode}")
                return False
        
        except Exception as e:
            self.logger.error(f"Runtime error in {self.mode} mode: {e}")
            return False
        finally:
            await self.shutdown()
        
        return True
    
    async def _run_cli_mode(self):
        """Run in CLI mode"""
        self.logger.info("Starting CLI interface...")
        await self.cli.start()
    
    async def _run_api_mode(self):
        """Run in API-only mode"""
        self.logger.info(f"Starting API server on {config.get('api.host')}:{config.get('api.port')}")
        
        uvicorn_config = uvicorn.Config(
            app=self.api,
            host=config.get('api.host', 'localhost'),
            port=config.get('api.port', 8000),
            log_level=config.get('logging.level', 'info').lower(),
            reload=config.get('nova.debug_mode', False)
        )
        
        server = uvicorn.Server(uvicorn_config)
        await server.serve()
    
    async def _run_web_mode(self):
        """Run in combined web + CLI mode"""
        self.logger.info("Starting web interface with CLI support...")
        
        # Start API server in background
        uvicorn_config = uvicorn.Config(
            app=self.api,
            host=config.get('api.host', 'localhost'),
            port=config.get('api.port', 8000),
            log_level=config.get('logging.level', 'info').lower()
        )
        
        server = uvicorn.Server(uvicorn_config)
        
        # Run server and CLI concurrently
        await asyncio.gather(
            server.serve(),
            self.cli.start(),
            self._wait_for_shutdown()
        )
    
    async def _run_daemon_mode(self):
        """Run in background daemon mode"""
        self.logger.info("Starting daemon mode...")
        
        # Start API server
        uvicorn_config = uvicorn.Config(
            app=self.api,
            host=config.get('api.host', 'localhost'),
            port=config.get('api.port', 8000),
            log_level=config.get('logging.level', 'info').lower()
        )
        
        server = uvicorn.Server(uvicorn_config)
        
        # Run until shutdown signal
        await asyncio.gather(
            server.serve(),
            self._wait_for_shutdown()
        )
    
    async def _wait_for_shutdown(self):
        """Wait for shutdown signal"""
        await self.shutdown_event.wait()
    
    async def shutdown(self):
        """Gracefully shutdown NOVA"""
        self.logger.info("Shutting down NOVA...")
        self.running = False
        
        # Shutdown components in reverse order
        if self.brain:
            await self.brain.shutdown()
        
        if self.security:
            await self.security.cleanup()
        
        self.logger.info("NOVA shutdown complete. Goodbye!")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="NOVA - Neural Omnipresent Virtual Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  cli     Interactive command-line interface (default)
  api     Web API server only
  web     Combined web interface and API
  daemon  Background service mode

Examples:
  python main.py                    # Start CLI mode
  python main.py --mode=api         # Start API server
  python main.py --mode=web         # Start web interface
  python main.py --mode=daemon      # Start as daemon
  python main.py --god-mode "scan system"  # Execute God Mode command
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["cli", "api", "web", "daemon", "god"],
        default="cli",
        help="Runtime mode (default: cli) - use 'god' for full hyper-intelligent capabilities"
    )
    
    parser.add_argument(
        "--personality", 
        default="assistant",
        choices=["professional", "casual", "hacker", "mentor", "creative", "analyst", "assistant"],
        help="Initial personality mode"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--god-mode",
        help="Execute God Mode instruction and exit"
    )
    
    parser.add_argument(
        "--host",
        help="API server host (overrides config)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        help="API server port (overrides config)"
    )
    
    return parser.parse_args()


async def execute_god_mode(instruction: str) -> bool:
    """Execute a God Mode instruction and exit"""
    try:
        nova = NOVAMain(mode="cli")
        if not await nova.initialize():
            return False
        
        print(f"🚀 Executing God Mode: {instruction}")
        result = await nova.brain.god_mode(instruction)
        print(f"✅ Result: {result}")
        
        await nova.shutdown()
        return True
        
    except Exception as e:
        logging.error(f"God Mode execution failed: {e}")
        return False


async def main():
    """Main entry point with next-generation capabilities"""
    args = parse_arguments()
    
    # Apply CLI argument overrides to config
    if args.debug:
        config.set('nova.debug_mode', True)
        config.set('logging.level', 'DEBUG')
    
    if args.personality:
        config.set('nova.personality', args.personality)
    
    if args.host:
        config.set('api.host', args.host)
    
    if args.port:
        config.set('api.port', args.port)
    
    if args.config:
        # Reload config from specified file
        config.config_path = Path(args.config)
        config.reload()
    
    # Handle God Mode execution
    if args.god_mode:
        success = await execute_god_mode(args.god_mode)
        sys.exit(0 if success else 1)
    
    # Handle God Mode deployment
    if args.mode == "god":
        print("🌟 Activating NOVA Hyper-Intelligent Ecosystem...")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🧠 Neural Evolution & Self-Learning")
        print("🌐 Universal API Integration") 
        print("🤖 Agent Swarm Intelligence")
        print("💖 Emotional Intelligence & Context")
        print("🛡️ AI Security Sentinel")
        print("🎯 Hyper-Intelligent Processing")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Enable all next-gen capabilities
        config.set('nova.god_mode', True)
        config.set('capabilities.neural_evolution', True)
        config.set('capabilities.swarm_intelligence', True)
        config.set('capabilities.emotional_engine', True)
        config.set('capabilities.security_sentinel', True)
        config.set('capabilities.universal_api', True)
    
    # Normal operation
    try:
        nova = NOVAMain(mode=args.mode)
        success = await nova.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 NOVA interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
