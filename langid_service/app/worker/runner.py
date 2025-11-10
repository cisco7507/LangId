# langid_service/app/worker/runner.py
import os
import json
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy.orm import Session
from loguru import logger
from ..database import SessionLocal
from ..models.models import Job, JobStatus
from ..config import MAX_RETRIES
from ..services.detector import detect_language

def _mock_detect(file_path: str):
    name = os.path.basename(file_path).lower()
    if "fr" in name:
        lang, prob = "fr", 0.95
    elif "en" in name:
        lang, prob = "en", 0.95
    else:
        lang, prob = "en", 0.6
    return {
        "language_raw": lang,
        "language_mapped": lang if lang in ("en","fr") else "unknown",
        "probability": float(prob),
        "transcript_snippet": None,
        "processing_ms": 1,
        "model": "mock",
        "info": {"duration": None, "vad": True},
    }

def process_one(session: Session, job: Job) -> None:
    logger.info(f"Processing job {job.id}")
    job.status = JobStatus.running
    job.progress = 10
    job.updated_at = datetime.now(UTC)
    session.commit()

    try:
        if os.environ.get("USE_MOCK_DETECTOR", "0") == "1":
            result = _mock_detect(job.input_path)
        else:
            result = detect_language(job.input_path)

        job.progress = 90
        session.commit()

        job.result_json = json.dumps(result)
        job.status = JobStatus.succeeded
        job.progress = 100
        job.updated_at = datetime.now(UTC)
        session.commit()
        logger.info(f"Job {job.id} succeeded")
    except Exception as e:
        logger.exception(f"Job {job.id} failed: {e}")
        job.attempts += 1
        job.error = str(e)
        job.status = JobStatus.queued if job.attempts <= MAX_RETRIES else JobStatus.failed
        job.updated_at = datetime.now(UTC)
        session.commit()

def work_once() -> Optional[str]:
    session = SessionLocal()
    try:
        job = session.query(Job).filter(Job.status == JobStatus.queued).order_by(Job.created_at.asc()).with_for_update().first()
        if not job:
            return None
        process_one(session, job)
        return job.id
    finally:
        session.close()
