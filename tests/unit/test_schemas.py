from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.project import ProjectRequest


def test_project_request_accepts_roadmap_id() -> None:
    request = ProjectRequest(roadmap_id="abc")

    assert request.roadmap_id == "abc"


def test_project_request_requires_valid_source() -> None:
    with pytest.raises(ValidationError):
        ProjectRequest(goal_title="AI")
