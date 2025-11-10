# langid_service/app/services/detector.py
import os
from typing import Dict, Any
from time import perf_counter

def _mock_detect(file_path: str) -> Dict[str, Any]:
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

def detect_language(file_path: str) -> Dict[str, Any]:
    # HARD GUARANTEE: if mock is enabled, never import faster-whisper or read audio
    if os.environ.get("USE_MOCK_DETECTOR", "0") == "1":
        return _mock_detect(file_path)

    # Lazy import here only for real path
    from time import perf_counter
    from faster_whisper import WhisperModel
    from ..config import WHISPER_MODEL_SIZE

    model = WhisperModel(WHISPER_MODEL_SIZE, device=os.environ.get("WHISPER_DEVICE", "cpu"),
                         compute_type=os.environ.get("WHISPER_COMPUTE", "int8"))
    t0 = perf_counter()
    segments, info = model.transcribe(
        file_path,
        beam_size=1,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
        language=None,
        task='transcribe',
        condition_on_previous_text=False,
        no_speech_threshold=0.6,
        temperature=0.0,
        initial_prompt=None,
    )
    lang = info.language
    prob = info.language_probability or 0.0
    mapped = 'en' if lang == 'en' else ('fr' if lang == 'fr' else 'unknown')
    snippet_words = []
    for seg in segments:
        if getattr(seg, "text", None):
            snippet_words.extend(seg.text.strip().split())
            if len(snippet_words) >= 15:
                break
    snippet = " ".join(snippet_words[:15]) if snippet_words else None
    elapsed_ms = int((perf_counter() - t0) * 1000)
    return {
        "language_raw": lang,
        "language_mapped": mapped,
        "probability": float(prob),
        "transcript_snippet": snippet,
        "processing_ms": elapsed_ms,
        "model": os.environ.get("WHISPER_MODEL_SIZE","small"),
        "info": {"duration": info.duration, "vad": True},
    }
