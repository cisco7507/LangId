import io
import wave
import struct
import math
import time


def make_tone_wav(duration_s=0.3, freq_hz=440.0, rate=16000):
    """Generate a small in-memory WAV tone (sine wave)."""
    samples = int(duration_s * rate)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        for i in range(samples):
            v = int(32767.0 * math.sin(2 * math.pi * freq_hz * i / rate))
            wf.writeframesraw(struct.pack("<h", v))
    wf.close()
    buf.seek(0)
    return buf


def test_submit_and_detect_en(client):
    # create a small valid wav buffer
    wav_buf = make_tone_wav()

    data = {"file": ("clip_en.wav", wav_buf, "audio/wav")}
    r = client.post("/jobs", files=data)
    assert r.status_code == 200, r.text
    job_id = r.json()["job_id"]
    assert r.json()["status"] == "queued"

    # poll for result
    status = None
    for _ in range(120):  # up to ~6s
        s = client.get(f"/jobs/{job_id}")
        assert s.status_code == 200
        js = s.json()
        status = js["status"]
        if status in ("succeeded", "failed"):
            break
        time.sleep(0.1)

    assert status == "succeeded", f"Job stuck in {status}"

    # confirm result endpoint works
    res = client.get(f"/jobs/{job_id}/result")
    assert res.status_code == 200, res.text
    js = res.json()
    assert "language" in js
    assert "probability" in js

def test_get_jobs(client):
    r = client.get("/jobs")
    assert r.status_code == 200, r.text
    js = r.json()
    assert "jobs" in js
    assert isinstance(js["jobs"], list)

def test_delete_job(client):
    # create a small valid wav buffer
    wav_buf = make_tone_wav()

    data = {"file": ("clip_en.wav", wav_buf, "audio/wav")}
    r = client.post("/jobs", files=data)
    assert r.status_code == 200, r.text
    job_id = r.json()["job_id"]

    # Delete the job
    r = client.request("DELETE", "/jobs", json={"job_ids": [job_id]})
    assert r.status_code == 200, r.text
    js = r.json()
    assert js["status"] == "ok"
    assert js["deleted_count"] == 1

    # Verify the job is gone
    r = client.get(f"/jobs/{job_id}")
    assert r.status_code == 404, r.text

def test_metrics_json(client):
    r = client.get("/metrics")
    assert r.status_code == 200, r.text
    js = r.json()
    assert "time_utc" in js
    assert "workers_configured" in js
    assert "model" in js
    assert "queue" in js
    assert js["model"]["size"] == "small"

def test_metrics_prometheus(client):
    r = client.get("/metrics/prometheus")
    assert r.status_code == 200, r.text
    text = r.text
    assert "langid_workers_configured" in text
    assert "langid_queue_total" in text
    assert "langid_model_info" in text