import json
import shutil
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
PORT = 8765
DB_PATH = DATA_DIR / "breathwork.db"
VIDEOS_DIR = DATA_DIR / "videos"
THUMBNAILS_DIR = DATA_DIR / "thumbnails"
THEME_CONFIG_PATH = DATA_DIR / "theme.json"


def _load_theme() -> str:
    if THEME_CONFIG_PATH.exists():
        try:
            with open(THEME_CONFIG_PATH) as f:
                data = json.load(f)
            return data.get("theme", "breathwork")
        except Exception:
            pass
    return "breathwork"


THEME = _load_theme()

FFMPEG_PATH = shutil.which("ffmpeg")
FFMPEG_AVAILABLE = FFMPEG_PATH is not None

DENO_PATH = shutil.which("deno")
DENO_AVAILABLE = DENO_PATH is not None
