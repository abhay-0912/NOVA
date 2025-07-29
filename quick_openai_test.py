import asyncio
import aiohttp
import os
from dotenv import load_dotenv

async def quick_openai_test():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"OpenAI API Key: {api_key[:20]}...")
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 20
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            print(f"Status: {response.status}")
            result = await response.text()
            print(f"Response: {result[:300]}...")

asyncio.run(quick_openai_test())
