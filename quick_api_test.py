import asyncio
import aiohttp
import os
from dotenv import load_dotenv

async def quick_gemini_test():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key: {api_key[:20]}...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    
    data = {
        "contents": [{"parts": [{"text": "Say hello"}]}],
        "generationConfig": {"maxOutputTokens": 20}
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            print(f"Status: {response.status}")
            result = await response.text()
            print(f"Response: {result[:200]}...")

asyncio.run(quick_gemini_test())
