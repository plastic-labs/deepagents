import aiohttp
from typing import List, Dict, Any, AsyncGenerator
import os
from dotenv import load_dotenv

load_dotenv()


class AnthropicClient:
    def __init__(self, api_key: str = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or .env file")
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"
    
    async def chat(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] = None, system: str = None, max_tokens: int = 4000) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages
        }
        
        if tools:
            payload["tools"] = tools
        
        if system:
            payload["system"] = system
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    raise Exception(f"API Error: {response.status} {await response.text()}")
                return await response.json()
    
    async def stream_chat(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] = None, max_tokens: int = 4000) -> AsyncGenerator[str, None]:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages,
            "stream": True
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = {"type": "auto"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload
            ) as response:
                async for line in response.content:
                    if line.startswith(b'data: '):
                        data = line[6:]
                        if data.strip() == b'[DONE]':
                            break
                        try:
                            yield data.decode('utf-8')
                        except:
                            continue


class LLMClient:
    def __init__(self, model: str = "claude-3-sonnet-20240229"):
        self.client = AnthropicClient(model=model)
    
    async def invoke(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] = None, system: str = None) -> Dict[str, Any]:
        return await self.client.chat(messages, tools, system)
    
    async def stream(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        async for chunk in self.client.stream_chat(messages, tools):
            yield chunk