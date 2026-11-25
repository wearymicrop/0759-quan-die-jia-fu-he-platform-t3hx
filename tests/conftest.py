import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.pipeline import process
from app.sources import load_sample


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "archive.sqlite3"))
    return TestClient(app)


@pytest.fixture(scope="session")
def dirty():
    return process(load_sample("dirty"))


@pytest.fixture(scope="session")
def clean():
    return process(load_sample("clean"))
