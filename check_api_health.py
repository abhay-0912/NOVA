"""
API Health Check - Test Gemini and OpenAI APIs directly

This script tests if the configured API keys are working properly
and helps diagnose connectivity issues.
"""

import asyncio
import aiohttp
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_gemini_api():
    """Test Gemini API connectivity and functionality"""
    print("🧪 Testing Gemini API...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No Gemini API key found in .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Hello! Please respond with 'API test successful' to confirm you're working."
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "candidateCount": 1,
            "maxOutputTokens": 50
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📡 Making API request to Gemini...")
            async with session.post(url, headers=headers, json=data) as response:
                print(f"📊 Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    if "candidates" in result and len(result["candidates"]) > 0:
                        content = result["candidates"][0]["content"]["parts"][0]["text"]
                        print(f"✅ Gemini API working! Response: {content}")
                        return True
                    else:
                        print("❌ Gemini API returned empty response")
                        print(f"Response: {result}")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Gemini API error {response.status}: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        return False

async def test_openai_api():
    """Test OpenAI API connectivity and functionality"""
    print("\n🧪 Testing OpenAI API...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OpenAI API key found in .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": "Hello! Please respond with 'API test successful' to confirm you're working."
            }
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📡 Making API request to OpenAI...")
            async with session.post(url, headers=headers, json=data) as response:
                print(f"📊 Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    print(f"✅ OpenAI API working! Response: {content}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ OpenAI API error {response.status}: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False

async def test_nova_ai_client():
    """Test NOVA's AI client with the configured APIs"""
    print("\n🧪 Testing NOVA AI Client...")
    
    try:
        from core.ai_client import AIClient, EnhancedQuestionAnswering
        
        # Test AI Client initialization
        ai_client = AIClient()
        print("✅ AI Client initialized")
        
        # Test Enhanced QA
        enhanced_qa = EnhancedQuestionAnswering()
        print("✅ Enhanced QA initialized")
        
        # Test simple question
        test_question = "What is 2+2?"
        print(f"🤔 Testing question: {test_question}")
        
        result = await enhanced_qa.answer_question(test_question)
        print(f"📋 Result status: {result['status']}")
        print(f"📋 Answer: {result['answer']}")
        print(f"📋 Model used: {result.get('model_used', 'unknown')}")
        
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
            return False
        else:
            print("✅ NOVA AI Client working!")
            return True
            
    except Exception as e:
        print(f"❌ NOVA AI Client failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_environment():
    """Check environment configuration"""
    print("\n⚙️ Checking Environment Configuration...")
    
    load_dotenv()
    
    config_items = [
        ("GEMINI_API_KEY", "Gemini API Key"),
        ("OPENAI_API_KEY", "OpenAI API Key"),
        ("DEFAULT_AI_MODEL", "Default AI Model"),
        ("GEMINI_MODEL", "Gemini Model"),
        ("FALLBACK_MODEL", "Fallback Model")
    ]
    
    for key, name in config_items:
        value = os.getenv(key, "not_set")
        if value and value != "not_set":
            if "API_KEY" in key:
                print(f"✅ {name}: {value[:10]}...{value[-4:]}")
            else:
                print(f"✅ {name}: {value}")
        else:
            print(f"❌ {name}: not configured")

async def main():
    """Main test routine"""
    print("🔍 NOVA API Health Check")
    print("=" * 50)
    
    # Check environment
    await check_environment()
    
    # Test APIs
    gemini_ok = await test_gemini_api()
    openai_ok = await test_openai_api()
    
    # Test NOVA integration
    nova_ok = await test_nova_ai_client()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 API Health Check Summary:")
    print(f"   Gemini API: {'✅ Working' if gemini_ok else '❌ Failed'}")
    print(f"   OpenAI API: {'✅ Working' if openai_ok else '❌ Failed'}")
    print(f"   NOVA AI Client: {'✅ Working' if nova_ok else '❌ Failed'}")
    
    if not (gemini_ok or openai_ok):
        print("\n🚨 No working APIs found!")
        print("💡 Troubleshooting tips:")
        print("   1. Check your API keys are correct and active")
        print("   2. Verify you have sufficient quota/credits")
        print("   3. Check your internet connection")
        print("   4. Try regenerating your API keys")
    elif nova_ok:
        print("\n🎉 NOVA AI is ready to use!")
    else:
        print("\n⚠️ APIs working but NOVA integration has issues")
        print("💡 Try restarting NOVA to reload configuration")

if __name__ == "__main__":
    asyncio.run(main())
