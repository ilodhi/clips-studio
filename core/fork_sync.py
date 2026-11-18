"""Git-based fork sync: pull from your origin, preview upstream merges.

Only runs inside a source checkout with `git` and `upstream` / `origin` remotes.
Packaged installs have no repo here; the API reports that instead of failing.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

# Files this fork usually touches; overlap with upstream since merge-base is
# a strong hint manual merge will be needed.
FORK_GUARD = frozenset({
    "video/outro.py",
    "server/api.py",
    "ui/src/renderer/src/pages/Settings.tsx",
    "ui/src/renderer/src/lib/api.ts",
    "ui/src/renderer/src/lib/types.ts",
    "config/settings.yaml",
    "config/fork.json",
    "ui/electron-builder.yml",
    "ui/src/main/updater.ts",
    "ui/src/main/fork.ts",
    "FORK.md",
    "AGENTS.md",
})

UPSTREAM_REF = "upstream/main"
ORIGIN_REF = "origin/main"


def repo_root() -> Path | None:
    """Walk up from this package for a `.git` directory."""
    here = Path(__file__).resolve().parent
    for parent in (here, *here.parents):
        if (parent / ".git").is_dir():
            return parent
        if parent == parent.parent:
            break
    return None


def _run(args: list[str], cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)


def _ok(r: subprocess.CompletedProcess[str]) -> bool:
    return r.returncode == 0


def is_fork_configured(root: Path) -> bool:
    return (root / "config" / "fork.json").is_file()


def _count_ahead_behind(cwd: Path, remote_ref: str) -> dict[str, int | None]:
    out: dict[str, int | None] = {"ahead": None, "behind": None}
    r = _run(["git", "rev-list", "--left-right", "--count", f"HEAD...{remote_ref}"], cwd)
    if not _ok(r):
        return out
    parts = r.stdout.strip().split()
    if len(parts) == 2:
        out["behind"] = int(parts[0])
        out["ahead"] = int(parts[1])
    return out


def _changed_files(cwd: Path, base: str, tip: str) -> set[str]:
    r = _run(["git", "diff", "--name-only", f"{base}...{tip}"], cwd)
    if not _ok(r):
        return set()
    return {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}


def fetch_remote(cwd: Path, remote: str) -> tuple[bool, str]:
    r = _run(["git", "fetch", remote], cwd, timeout=300)
    if _ok(r):
        return True, ""
    return False, (r.stderr or r.stdout or "fetch failed").strip()[-400:]


def status() -> dict:
    root = repo_root()
    if root is None:
        return {
            "enabled": False,
            "reason": "not_a_git_checkout",
            "message": "Fork git sync works when you run from a cloned repository, not from a packaged installer.",
        }
    if not is_fork_configured(root):
        return {"enabled": False, "reason": "no_fork_config", "message": "No config/fork.json in this checkout."}
    fetch_remote(root, "origin")
    fetch_remote(root, "upstream")
    upstream = _count_ahead_behind(root, UPSTREAM_REF)
    origin = _count_ahead_behind(root, ORIGIN_REF)
    dirty = _run(["git", "status", "--porcelain"], root).stdout.strip()
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], root).stdout.strip()
    return {
        "enabled": True,
        "root": str(root),
        "branch": branch,
        "dirty": bool(dirty),
        "upstream": {"ref": UPSTREAM_REF, **upstream},
        "origin": {"ref": ORIGIN_REF, **origin},
    }


def check_upstream() -> dict:
    root = repo_root()
    if not root:
        return {"ok": False, "error": "Not a git checkout."}
    ok, err = fetch_remote(root, "upstream")
    if not ok:
        return {"ok": False, "error": f"Could not fetch upstream: {err}"}
    base = _run(["git", "merge-base", "HEAD", UPSTREAM_REF], root).stdout.strip()
    if not base:
        return {"ok": False, "error": "Could not find a merge-base with upstream."}
    ours = _changed_files(root, base, "HEAD")
    theirs = _changed_files(root, base, UPSTREAM_REF)
    overlap = sorted(ours & theirs)
    fork_critical = sorted((ours & theirs) & FORK_GUARD)
    behind = _count_ahead_behind(root, UPSTREAM_REF).get("behind") or 0

    merge_conflicts: bool | None = None
    merge_tree = _run(["git", "merge-tree", "--write-tree", "HEAD", UPSTREAM_REF], root)
    if merge_tree.returncode not in (0, 1):
        merge_conflicts = None
    else:
        merge_conflicts = merge_tree.returncode != 0 or "CONFLICT" in merge_tree.stdout

    safe = behind == 0 or (not overlap and merge_conflicts is not True)
    return {
        "ok": True,
        "behind": behind,
        "merge_base": base[:12],
        "overlap": overlap,
        "fork_critical": fork_critical,
        "merge_conflicts": merge_conflicts,
        "safe_to_merge": safe and not fork_critical and merge_conflicts is not True,
        "recommendation": (
            "Nothing new on upstream."
            if behind == 0
            else (
                "No overlapping files — merge upstream should apply cleanly."
                if not overlap and merge_conflicts is not True
                else "Review overlapping files before merging; resolve conflicts in git after."
            )
        ),
    }


def pull_origin() -> dict:
    root = repo_root()
    if not root:
        return {"ok": False, "error": "Not a git checkout."}
    if _run(["git", "status", "--porcelain"], root).stdout.strip():
        return {"ok": False, "error": "Commit or stash local changes before pulling."}
    ok, err = fetch_remote(root, "origin")
    if not ok:
        return {"ok": False, "error": f"Could not fetch origin: {err}"}
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], root).stdout.strip() or "main"
    r = _run(["git", "pull", "--ff-only", "origin", branch], root, timeout=300)
    if not _ok(r):
        return {"ok": False, "error": (r.stderr or r.stdout or "pull failed").strip()[-500:]}
    return {
        "ok": True,
        "message": f"Pulled latest from origin/{branch}. Restart the app if Python or UI files changed.",
    }


def merge_upstream(*, allow_overlap: bool = False) -> dict:
    root = repo_root()
    if not root:
        return {"ok": False, "error": "Not a git checkout."}
    if _run(["git", "status", "--porcelain"], root).stdout.strip():
        return {"ok": False, "error": "Commit or stash local changes before merging upstream."}
    preview = check_upstream()
    if not preview.get("ok"):
        return preview
    if preview.get("behind", 0) == 0:
        return {"ok": True, "message": "Already up to date with upstream."}
    if not allow_overlap and not preview.get("safe_to_merge"):
        return {
            "ok": False,
            "error": "Upstream merge is not safe (overlapping or conflicting files). Resolve in git, or check again after committing.",
            "preview": preview,
        }
    ok, err = fetch_remote(root, "upstream")
    if not ok:
        return {"ok": False, "error": err}
    r = _run(["git", "merge", "--no-edit", UPSTREAM_REF], root, timeout=300)
    if not _ok(r):
        _run(["git", "merge", "--abort"], root)
        return {
            "ok": False,
            "error": (r.stderr or r.stdout or "merge failed").strip()[-500:],
            "hint": "Merge aborted. Resolve conflicts in a terminal with git status.",
        }
    return {
        "ok": True,
        "message": "Merged upstream/main. Restart the app. If npm or Python deps changed, reinstall them.",
    }


def fork_json_summary(root: Path) -> dict | None:
    path = root / "config" / "fork.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None