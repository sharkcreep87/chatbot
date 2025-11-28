from typing import List, Dict, Any, AsyncGenerator
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from app.core.config import settings


class AIService:
    """Service for interacting with AI providers"""

    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None

        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        provider: str = "openai",
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Dict[str, Any]:
        """Generate a response from the AI provider"""
        if provider == "openai":
            return await self._generate_openai_response(messages, model, temperature, max_tokens)
        elif provider == "anthropic":
            return await self._generate_anthropic_response(messages, model, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

    async def generate_stream_response(
        self,
        messages: List[Dict[str, str]],
        provider: str = "openai",
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the AI provider"""
        if provider == "openai":
            async for chunk in self._generate_openai_stream(messages, model, temperature, max_tokens):
                yield chunk
        elif provider == "anthropic":
            async for chunk in self._generate_anthropic_stream(messages, model, temperature, max_tokens):
                yield chunk
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

    async def _generate_openai_response(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return {
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "finish_reason": response.choices[0].finish_reason,
        }

    async def _generate_anthropic_response(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """Generate response using Anthropic Claude"""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")

        # Convert messages format for Anthropic
        system_message = ""
        formatted_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        response = await self.anthropic_client.messages.create(
            model=model if "claude" in model else "claude-3-opus-20240229",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message if system_message else None,
            messages=formatted_messages,
        )

        return {
            "content": response.content[0].text,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            "finish_reason": response.stop_reason,
        }

    async def _generate_openai_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using OpenAI"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        stream = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def _generate_anthropic_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using Anthropic Claude"""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")

        # Convert messages format for Anthropic
        system_message = ""
        formatted_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        async with self.anthropic_client.messages.stream(
            model=model if "claude" in model else "claude-3-opus-20240229",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message if system_message else None,
            messages=formatted_messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text


# Create singleton instance
ai_service = AIService()
