from __future__ import annotations

from app.utils.json import extract_json_object


def test_extract_json_object_from_fenced_response() -> None:
    payload = extract_json_object('```json\n{"response": "ok"}\n```')

    assert payload == {"response": "ok"}


def test_extract_json_object_from_surrounding_text() -> None:
    payload = extract_json_object('Here is the JSON: {"answer": 42} Thanks.')

    assert payload == {"answer": 42}
