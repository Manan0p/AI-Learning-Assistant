from __future__ import annotations

import pytest

from app.schemas.chat import ChatLLMOutput
from app.services.gemini import GeminiService


class FakeGemini(GeminiService):
    def __init__(self) -> None:
        self.calls = 0

    async def _generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        if self.calls == 1:
            return "not-json"
        return '{"response": "Study APIs first.", "follow_up_questions": ["How many hours?"]}'

    async def _get_cached(self, key: str) -> str | None:
        return None

    async def _set_cached(self, key: str, value: str) -> None:
        return None


@pytest.mark.asyncio
async def test_generate_validated_json_retries_malformed_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def no_sleep(_: float) -> None:
        return None

    monkeypatch.setattr("app.services.gemini.asyncio.sleep", no_sleep)
    service = FakeGemini()

    result = await service.generate_validated_json(
        system_prompt="system",
        user_prompt="user",
        response_model=ChatLLMOutput,
    )

    assert service.calls == 2
    assert result.response == "Study APIs first."
