# langid_service/app/metrics.py
from prometheus_client import Counter, Histogram, Gauge, REGISTRY

# --- Unregister metrics before defining them ---
for collector in list(REGISTRY._collector_to_names.keys()):
    if 'langid' in REGISTRY._collector_to_names[collector]:
        REGISTRY.unregister(collector)

# --- Job Status Counter ---
LANGID_JOBS_TOTAL = Counter(
    "langid_jobs_total",
    "Total number of jobs processed",
    ["status"]  # Labels: "succeeded", "failed", "invalid_audio"
)

# --- Inference Duration Histogram ---
LANGID_INFER_DURATION_MS = Histogram(
    "langid_infer_duration_ms",
    "Inference duration in milliseconds",
    buckets=[100, 250, 500, 1000, 2500, 5000, 10000]
)

# --- Audio Decoding Failure Counter ---
LANGID_DECODE_FAIL_TOTAL = Counter(
    "langid_decode_fail_total",
    "Total number of audio decoding failures"
)

# --- Language Probability Gauge ---
LANGID_LANG_PROBABILITY = Gauge(
    "langid_lang_probability",
    "Probability of the detected language",
    ["lang"]
)
