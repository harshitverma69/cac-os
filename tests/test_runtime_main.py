"""Test runtime __main__ entrypoint."""

import sys

from runtime import __main__ as runtime_main


def test_runtime_main_requires_args(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["runtime"])
    assert runtime_main.main() == 1


def test_runtime_main_plan_only(capsys, monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["runtime", "--plan-only", "--skill", "B3", "--run-id", "main-test"],
    )
    assert runtime_main.main() == 0
