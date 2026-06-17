"""Shared pytest configuration."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def disable_auto_skill_ui(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep test stdout clean; UI hook tests opt in explicitly."""
    monkeypatch.setenv("REPO_ANALYSER_AUTO_SKILL_DONE", "0")
    monkeypatch.setenv("REPO_ANALYSER_AUTO_FRONTEND", "0")
    monkeypatch.setenv("REPO_ANALYSER_AUTO_START_FRONTEND", "0")
