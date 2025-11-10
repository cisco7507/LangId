from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR.parent / "storage"
LOG_DIR = BASE_DIR.parent / "logs"

# SQLite DB file
DB_URL = f"sqlite:///{(BASE_DIR / 'langid.sqlite').as_posix()}"

# Model size: 'tiny', 'base', 'small', 'medium', 'large-v3'
WHISPER_MODEL_SIZE = "small"

# Max concurrent worker jobs
MAX_WORKERS = 2

# Retry policy
MAX_RETRIES = 2

# File size limit (bytes) ~ 100 MB
MAX_UPLOAD_BYTES = 1000 * 1024 * 1024

# Allowed extensions
ALLOWED_EXTS = {".wav", ".wave"}
