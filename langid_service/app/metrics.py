# app/metrics.py
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry

# Single, app-scoped registry (not the global default REGISTRY)
APP_REGISTRY = CollectorRegistry(auto_describe=True)

# Define all metrics with `registry=APP_REGISTRY`
LANGID_JOBS_TOTAL = Counter(
    "langid_jobs_total",
    "Jobs processed by status",
    ["status"],  # e.g., queued|running|succeeded|failed
    registry=APP_REGISTRY,
)

LANGID_JOBS_RUNNING = Gauge(
    "langid_jobs_running",
    "Number of jobs currently running",
    registry=APP_REGISTRY,
)

LANGID_PROCESSING_SECONDS = Histogram(
    "langid_processing_seconds",
    "End-to-end processing latency per job",
    buckets=(0.5, 1, 2, 5, 10, 20, 30, 60, 120, 300),
    registry=APP_REGISTRY,
)

LANGID_ACTIVE_WORKERS = Gauge(
    "langid_active_workers",
    "Number of active worker threads",
    registry=APP_REGISTRY,
)

LANGID_AUDIO_SECONDS = Histogram(
    "langid_audio_seconds",
    "Input audio duration per job (seconds)",
    buckets=(1, 3, 10, 30, 60, 120, 300, 900, 1800),
    registry=APP_REGISTRY,
)

# …add any other metrics here, always with registry=APP_REGISTRY


def _swap_registry_for_tests(new_registry):
    """Testing helper: rebind metric objects to a fresh registry."""
    global APP_REGISTRY, LANGID_JOBS_TOTAL, LANGID_JOBS_RUNNING, LANGID_PROCESSING_SECONDS, LANGID_ACTIVE_WORKERS, LANGID_AUDIO_SECONDS
    APP_REGISTRY = new_registry

    LANGID_JOBS_TOTAL = Counter("langid_jobs_total", "Jobs processed by status", ["status"], registry=APP_REGISTRY)
    LANGID_JOBS_RUNNING = Gauge("langid_jobs_running", "Number of jobs currently running", registry=APP_REGISTRY)
    LANGID_PROCESSING_SECONDS = Histogram("langid_processing_seconds", "End-to-end processing latency per job",
                                          buckets=(0.5, 1, 2, 5, 10, 20, 30, 60, 120, 300),
                                          registry=APP_REGISTRY)
    LANGID_ACTIVE_WORKERS = Gauge("langid_active_workers", "Number of active worker threads", registry=APP_REGISTRY)
    LANGID_AUDIO_SECONDS = Histogram("langid_audio_seconds", "Input audio duration per job (seconds)",
                                     buckets=(1, 3, 10, 30, 60, 120, 300, 900, 1800),
                                     registry=APP_REGISTRY)
