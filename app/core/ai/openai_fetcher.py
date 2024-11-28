"""Module to connect to openai api."""
from typing import Type

from openai import AsyncOpenAI
from pydantic import BaseModel

from config import OPEN_AI_TOKEN


class OpenAiFetcher:
    """Handler for OpenAi api calls."""

    def __init__(self, api_key=None):
        """Init of OpenAiFetcher."""
        self.api_key = api_key or OPEN_AI_TOKEN
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.current_batch_jobs = {}

    async def get_output(self, messages, model="gpt-4o-mini", temperature=0.3):
        """Get output of model."""
        response = await self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages,
        )
        return response.choices[0].message.content

    async def get_json_output(
        self,
        messages,
        response_format: Type[BaseModel],
        model="gpt-4o-mini",
        temperature=0.3,
    ):
        """Get output of model in the format of response_format."""
        response = await self.client.beta.chat.completions.parse(
            model=model,
            temperature=temperature,
            messages=messages,
            response_format=response_format,
        )
        return response.choices[0].message.parsed

    async def get_streamed_output(self, messages, model="gpt-4o-mini", temperature=0.3):
        """Get streamed output of model."""
        response = await self.client.chat.completions.create(
            model=model, temperature=temperature, messages=messages, stream=True
        )

        async for chunk in response:
            text = chunk.choices[0].delta.content
            if text:
                yield text
