import os
from typing import Any, AsyncGenerator

import aiohttp
from dotenv import load_dotenv

load_dotenv()


class AnthropicClient:
    def __init__(self, api_key: str = None, model: str = "claude-4-sonnet-20250514"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or .env file")
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] = None,
        system: str = None,
        max_tokens: int = 4000,
    ) -> dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        payload = {"model": self.model, "max_tokens": max_tokens, "messages": messages}

        if tools:
            payload["tools"] = tools

        if system:
            payload["system"] = system

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/messages", headers=headers, json=payload
            ) as response:
                if response.status != 200:
                    raise Exception(
                        f"API Error: {response.status} {await response.text()}"
                    )
                return await response.json()

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] = None,
        max_tokens: int = 4000,
    ) -> AsyncGenerator[str, None]:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages,
            "stream": True,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = {"type": "auto"}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/messages", headers=headers, json=payload
            ) as response:
                async for line in response.content:
                    if line.startswith(b"data: "):
                        data = line[6:]
                        if data.strip() == b"[DONE]":
                            break
                        try:
                            yield data.decode("utf-8")
                        except Exception:
                            continue


class LLMClient:
    def __init__(self, model: str = "claude-4-sonnet-20250514"):
        self.client = AnthropicClient(model=model)

    async def invoke(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] = None,
        system: str = None,
    ) -> dict[str, Any]:
        return await self.client.chat(messages, tools, system)

    async def stream(
        self, messages: list[dict[str, str]], tools: list[dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        async for chunk in self.client.stream_chat(messages, tools):
            yield chunk
