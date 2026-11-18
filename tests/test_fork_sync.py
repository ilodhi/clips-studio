"""Fork git sync helpers (status, upstream preview) for ilodhi builds."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def mini_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=repo, check=True)
    (repo / "config").mkdir()
    (repo / "config" / "fork.json").write_text('{"updates": false}', encoding="utf-8")
    (repo / "readme.txt").write_text("v1\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)
    return repo


def test_status_enabled_in_fork_checkout(mini_repo, monkeypatch):
    from core import fork_sync

    monkeypatch.setattr(fork_sync, "repo_root", lambda: mini_repo)
    monkeypatch.setattr(fork_sync, "fetch_remote", lambda *_a, **_k: (True, ""))
    monkeypatch.setattr(
        fork_sync,
        "_count_ahead_behind",
        lambda *_a, **_k: {"ahead": 0, "behind": 0},
    )
    s = fork_sync.status()
    assert s["enabled"] is True
    assert s["branch"] == "main"


def test_merge_upstream_refuses_without_safe_preview(mini_repo, monkeypatch):
    from core import fork_sync

    monkeypatch.setattr(fork_sync, "repo_root", lambda: mini_repo)
    monkeypatch.setattr(
        fork_sync,
        "check_upstream",
        lambda: {
            "ok": True,
            "behind": 3,
            "safe_to_merge": False,
            "fork_critical": ["video/outro.py"],
            "overlap": ["video/outro.py"],
        },
    )
    r = fork_sync.merge_upstream(allow_overlap=False)
    assert r["ok"] is False
    assert "not safe" in r["error"].lower()