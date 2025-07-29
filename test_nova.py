"""
Test script to verify NOVA setup and basic functionality
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.brain import NOVABrain, NOVAConfig


async def test_nova_basic_functionality():
    """Test basic NOVA functionality"""
    
    print("🧠 Testing NOVA Basic Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Configuration
        print("\n1. Testing configuration...")
        config = NOVAConfig(
            name="NOVA-Test",
            personality="assistant",
            debug_mode=True,
            voice_enabled=False,  # Disable for testing
            vision_enabled=False,  # Disable for testing
            local_mode=True
        )
        print("✅ Configuration created successfully")
        
        # Test 2: Brain initialization
        print("\n2. Testing brain initialization...")
        brain = NOVABrain(config)
        init_success = await brain.initialize()
        
        if init_success:
            print("✅ NOVA brain initialized successfully")
        else:
            print("❌ NOVA brain initialization failed")
            return False
        
        # Test 3: Get status
        print("\n3. Testing status retrieval...")
        status = await brain.get_status()
        print(f"   State: {status.get('state', 'unknown')}")
        print(f"   Capabilities: {len(status.get('capabilities', {}))}")
        print("✅ Status retrieved successfully")
        
        # Test 4: Process simple input
        print("\n4. Testing input processing...")
        test_input = {
            "type": "text",
            "content": "Hello NOVA, can you help me?",
            "context": {"test": True}
        }
        
        response = await brain.process_input(test_input)
        print(f"   Response: {response.get('response', 'No response')[:100]}...")
        print("✅ Input processed successfully")
        
        # Test 5: God mode (basic test)
        print("\n5. Testing god mode...")
        god_result = await brain.god_mode("Create a simple test plan")
        print(f"   God mode status: {god_result.get('status', 'unknown')}")
        print("✅ God mode tested successfully")
        
        # Test 6: Cleanup
        print("\n6. Testing cleanup...")
        await brain.shutdown()
        print("✅ Cleanup completed successfully")
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! NOVA is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False


async def test_components():
    """Test individual components"""
    
    print("\n🔧 Testing Individual Components")
    print("=" * 50)
    
    try:
        # Test memory system
        print("\n1. Testing memory system...")
        from core.memory import MemorySystem
        
        memory = MemorySystem("test_memory.db")
        await memory.initialize()
        
        # Test storing and retrieving
        memory_id = await memory.store_interaction({
            "content": "Test interaction",
            "type": "test"
        })
        
        if memory_id:
            print("✅ Memory system working")
        
        await memory.cleanup()
        
        # Test personality engine
        print("\n2. Testing personality engine...")
        from core.personality import PersonalityEngine
        
        personality = PersonalityEngine("assistant")
        await personality.initialize()
        
        style = personality.get_response_style({"type": "casual"})
        if style:
            print("✅ Personality engine working")
        
        # Test orchestrator
        print("\n3. Testing orchestrator...")
        from core.orchestrator import AgentOrchestrator
        
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        agents = await orchestrator.get_active_agents()
        print(f"   Active agents: {len(agents)}")
        print("✅ Orchestrator working")
        
        await orchestrator.shutdown()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Component test failed: {e}")
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    
    print("🚀 NOVA Test Suite")
    print("Testing NOVA functionality and components")
    print("=" * 60)
    
    # Test basic functionality
    basic_test_passed = await test_nova_basic_functionality()
    
    # Test components
    component_test_passed = await test_components()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Basic functionality: {'✅ PASSED' if basic_test_passed else '❌ FAILED'}")
    print(f"Component tests: {'✅ PASSED' if component_test_passed else '❌ FAILED'}")
    
    if basic_test_passed and component_test_passed:
        print("\n🎉 All tests passed! NOVA is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python main.py' to start NOVA")
        print("2. Visit http://localhost:8000 for web interface")
        print("3. Use 'python main.py --help' for more options")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check Python version (3.9+ required)")
        print("3. Review error messages for specific issues")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
