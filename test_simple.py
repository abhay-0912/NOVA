#!/usr/bin/env python3
"""
Simple NOVA test launcher
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.brain import NOVABrain, NOVAConfig

async def main():
    """Simple test of NOVA brain"""
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Creating NOVA config...")
        config = NOVAConfig()
        
        logger.info("Initializing NOVA brain...")
        brain = NOVABrain(config)
        await brain.initialize()
        
        logger.info("NOVA initialized successfully!")
        
        # Test basic functionality
        logger.info("Testing NOVA...")
        response = await brain.process_input("Hello NOVA! Can you introduce yourself?")
        print(f"\nNOVA Response: {response}\n")
        
        # Test God Mode
        logger.info("Testing God Mode...")
        god_response = await brain.god_mode("Check system status and tell me what you can do")
        print(f"\nGod Mode Response: {god_response}\n")
        
        logger.info("NOVA test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
