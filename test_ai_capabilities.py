"""
Test Enhanced AI Capabilities in NOVA

This script tests the new Gemini-powered AI enhancements
by directly testing the AI client and enhanced question answering.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

async def test_ai_capabilities():
    """Test the enhanced AI capabilities"""
    
    print("🧪 Testing NOVA's Enhanced AI Capabilities")
    print("=" * 50)
    
    # Test 1: Import the AI Client
    try:
        from core.ai_client import EnhancedQuestionAnswering, AIClient
        print("✅ AI Client imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AI Client: {e}")
        return
    
    # Test 2: Initialize Enhanced QA
    try:
        enhanced_qa = EnhancedQuestionAnswering()
        print("✅ Enhanced Question Answering initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Enhanced QA: {e}")
        return
    
    # Test 3: Test Question Classification
    test_questions = [
        "What is 2 + 2?",
        "What is artificial intelligence?", 
        "How does machine learning work?",
        "Create a poem about the ocean",
        "Analyze the benefits of renewable energy"
    ]
    
    print("\n🔍 Testing Question Classification:")
    for question in test_questions:
        question_type = enhanced_qa._classify_question(question)
        print(f"   '{question}' → {question_type}")
    
    # Test 4: Test AI Response (without requiring API keys)
    print("\n🤖 Testing AI Response Generation:")
    
    # Test with fallback (no API keys configured)
    test_question = "What is artificial intelligence?"
    try:
        result = await enhanced_qa.answer_question(test_question)
        print(f"✅ AI Response generated successfully")
        print(f"   Question: {result['question']}")
        print(f"   Type: {result['type']}")
        print(f"   Status: {result['status']}")
        print(f"   Answer: {result['answer'][:100]}...")
        if result.get('model_used'):
            print(f"   Model: {result['model_used']}")
    except Exception as e:
        print(f"❌ AI Response failed: {e}")
    
    # Test 5: Test Orchestrator Integration
    print("\n🎭 Testing Orchestrator Integration:")
    try:
        from core.orchestrator import ResearchAgent
        research_agent = ResearchAgent()
        print("✅ Research Agent created")
        
        # Check if enhanced capabilities are available
        if hasattr(research_agent, 'enhanced_qa') and research_agent.enhanced_qa:
            print("✅ Enhanced AI capabilities integrated into Research Agent")
        else:
            print("⚠️  Enhanced AI capabilities not integrated (may require API keys)")
            
    except Exception as e:
        print(f"❌ Orchestrator integration test failed: {e}")
    
    # Test 6: Configuration Check
    print("\n⚙️  Testing Configuration:")
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        gemini_key = os.getenv("GEMINI_API_KEY", "not_set")
        default_model = os.getenv("DEFAULT_AI_MODEL", "not_set")
        
        print(f"   Default AI Model: {default_model}")
        print(f"   Gemini API Key: {'configured' if gemini_key != 'not_set' and gemini_key else 'not configured'}")
        
        if gemini_key == "not_set" or not gemini_key:
            print("   💡 Tip: Set GEMINI_API_KEY in .env file for full AI capabilities")
            
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
    
    # Cleanup
    try:
        await enhanced_qa.close()
        print("\n✅ AI Client closed successfully")
    except:
        pass
    
    print("\n🎉 Enhanced AI Capabilities Test Complete!")
    print("\nTo use the enhanced AI capabilities:")
    print("1. Get a Gemini API key from https://makersuite.google.com/app/apikey")
    print("2. Copy .env.example to .env")
    print("3. Set GEMINI_API_KEY=your_api_key_here in .env")
    print("4. Restart NOVA and enjoy enhanced AI responses!")

if __name__ == "__main__":
    asyncio.run(test_ai_capabilities())
