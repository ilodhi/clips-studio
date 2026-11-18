"""Settings and upload endpoints for a custom clip end card."""

import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def api(tmp_path, monkeypatch):
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient

    from main import BUNDLED_CONFIG, load_config
    from server.api import create_app

    settings = tmp_path / "settings.yaml"
    shutil.copy(ROOT / "config" / "settings.yaml", settings)
    config = load_config(BUNDLED_CONFIG)
    config["paths"]["data_dir"] = str(tmp_path / "data")
    app = create_app(config, settings)
    return TestClient(app, base_url="http://127.0.0.1")


def test_settings_round_trip_custom_outro(api):
    assert api.get("/settings").json()["custom_outro"] == ""

    r = api.patch("/settings", json={"custom_outro": "abc123.mp4"})
    assert r.status_code == 200
    assert api.get("/settings").json()["custom_outro"] == "abc123.mp4"

    r = api.patch("/settings", json={"custom_outro": ""})
    assert r.status_code == 200
    assert api.get("/settings").json()["custom_outro"] == ""


def test_settings_rejects_traversal_in_custom_outro(api):
    assert api.patch("/settings", json={"custom_outro": "../evil.mp4"}).status_code == 400