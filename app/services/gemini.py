from __future__ import annotations

import asyncio
from typing import Any, TypeVar

from google import genai
from google.genai import types
from loguru import logger
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.exceptions import LLMOutputError
from app.services.cache import cache_key, get_redis
from app.utils.json import extract_json_object

ModelT = TypeVar("ModelT", bound=BaseModel)


class GeminiService:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.google_api_key)

    async def generate_validated_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[ModelT],
        cache_prefix: str | None = None,
    ) -> ModelT:
        cache_id = cache_key(cache_prefix, user_prompt) if cache_prefix else None
        if cache_id:
            cached = await self._get_cached(cache_id)
            if cached:
                return response_model.model_validate_json(cached)

        last_error: Exception | None = None
        for attempt in range(1, settings.llm_max_retries + 1):
            try:
                text = await self._generate(system_prompt=system_prompt, user_prompt=user_prompt)
                payload = extract_json_object(text)
                parsed = response_model.model_validate(payload)
                if cache_id:
                    await self._set_cached(cache_id, parsed.model_dump_json())
                return parsed
            except (ValidationError, ValueError) as exc:
                last_error = exc
                if attempt == settings.llm_max_retries:
                    break
                sleep_for = min(2 ** (attempt - 1), 8)
                logger.debug("Retrying malformed LLM output in {} seconds", sleep_for)
                await asyncio.sleep(sleep_for)

        logger.warning("LLM validation failed after retries: {}", last_error)
        raise LLMOutputError()

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = await self.client.aio.models.embed_content(
            model=settings.embedding_model,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=settings.embedding_dimensions,
            ),
        )
        return [embedding.values for embedding in response.embeddings or []]

    async def embed_query(self, text: str) -> list[float]:
        response = await self.client.aio.models.embed_content(
            model=settings.embedding_model,
            contents=[text],
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=settings.embedding_dimensions,
            ),
        )
        embeddings = response.embeddings or []
        if not embeddings:
            raise LLMOutputError("Embedding service returned no vector.")
        return embeddings[0].values

    async def _generate(self, *, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.4,
            ),
        )
        if not response.text:
            raise LLMOutputError("Gemini returned an empty response.")
        return response.text

    async def _get_cached(self, key: str) -> str | None:
        try:
            redis = await get_redis()
            value: Any = await redis.get(key)
            return value if isinstance(value, str) else None
        except Exception as exc:
            logger.debug("Redis read skipped: {}", exc)
            return None

    async def _set_cached(self, key: str, value: str) -> None:
        try:
            redis = await get_redis()
            await redis.set(key, value, ex=60 * 60)
        except Exception as exc:
            logger.debug("Redis write skipped: {}", exc)
