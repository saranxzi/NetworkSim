"""Backend test fixtures: isolated SQLite DB, app with lifespan started."""
import os
import sys
import tempfile
from pathlib import Path

# Must be set before app modules are imported (db.py reads env at import time)
_TMP_DB_DIR = tempfile.mkdtemp(prefix="networksim_test_")
_DB_PATH = Path(_TMP_DB_DIR) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_DB_PATH.as_posix()}"
os.environ["AUTH_ENABLED"] = "false"
os.environ["REDIS_URL"] = ""
os.environ["ENVIRONMENT"] = "test"

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    from app.main import app
    with TestClient(app) as test_client:
        yield test_client
