import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

async def test_fallback_responses():
    print("🧪 Testing Enhanced Fallback Responses")
    print("=" * 40)
    
    from core.ai_client import EnhancedQuestionAnswering, AIModelType
    
    enhanced_qa = EnhancedQuestionAnswering()
    
    test_questions = [
        "Hello!",
        "What is 2+2?",
        "What is artificial intelligence?",
        "Test NOVA functionality",
        "Help me with programming",
        "What can you do?"
    ]
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        result = await enhanced_qa.answer_question(question)
        print(f"📋 Answer: {result['answer']}")
        print(f"🤖 Model: {result.get('model_used', 'unknown')}")
        print(f"📊 Status: {result['status']}")
        
    await enhanced_qa.close()
    print("\n✅ Test complete!")

asyncio.run(test_fallback_responses())
