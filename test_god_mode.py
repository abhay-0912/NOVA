"""
Test God Mode with Enhanced Fallback Responses

This script simulates God Mode interactions to test
the enhanced AI fallback system.
"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

async def test_god_mode_responses():
    print("👑 Testing God Mode with Enhanced Fallback")
    print("=" * 50)
    
    from core.orchestrator import ResearchAgent, Task, AgentType
    
    # Create research agent (same as God Mode uses)
    research_agent = ResearchAgent()
    
    # Test God Mode style questions
    test_cases = [
        {
            "description": "Math question", 
            "parameters": {
                "action": "answer_question",
                "question": "What is 2+2?",
                "type": "mathematical"
            }
        },
        {
            "description": "AI knowledge question",
            "parameters": {
                "action": "answer_question", 
                "question": "What is artificial intelligence?",
                "type": "factual"
            }
        },
        {
            "description": "Greeting response",
            "parameters": {
                "action": "respond",
                "message": "Hello NOVA",
                "type": "greeting"
            }
        },
        {
            "description": "Test functionality",
            "parameters": {
                "action": "respond",
                "message": "Test NOVA",
                "type": "test"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['description']}")
        
        # Create task like God Mode does
        from datetime import datetime
        task = Task(
            id=f"test-{i}",
            type=AgentType.RESEARCH,
            description=test_case['description'],
            priority=1,
            parameters=test_case['parameters'],
            created_at=datetime.now()
        )
        
        try:
            result = await research_agent.execute_task(task)
            
            print(f"📋 Status: {result.get('status', 'unknown')}")
            print(f"🤖 Answer: {result.get('answer', 'No answer provided')}")
            
            if result.get('explanation'):
                print(f"💡 Explanation: {result.get('explanation')}")
                
            if result.get('model_used'):
                print(f"🔧 Model: {result.get('model_used')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 God Mode testing complete!")
    print("\n💡 To test interactively:")
    print("   1. Start NOVA: python main.py")
    print("   2. Try these commands:")
    print("      • Hello")
    print("      • What is 2+2?") 
    print("      • What is artificial intelligence?")
    print("      • Test")

if __name__ == "__main__":
    asyncio.run(test_god_mode_responses())
