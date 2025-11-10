# langid_service/tests/conftest.py
import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from prometheus_client import REGISTRY

# IMPORTANT: set mock before importing app so workers inherit it
os.environ["USE_MOCK_DETECTOR"] = "1"

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402

@pytest.fixture(autouse=True)
def unregister_prometheus_collectors():
    """
    Unregister all Prometheus collectors before each test.
    This prevents errors when the tests are run in parallel.
    """
    for collector in list(REGISTRY._collector_to_names.keys()):
        REGISTRY.unregister(collector)
    yield

@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
