from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import config
from .database import init_db
from .routers import downloads, system, videos
from .services.downloader import download_service
from .themes import get_theme

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    if not config.FFMPEG_AVAILABLE:
        logger.warning(
            "ffmpeg not found! Video downloads will fail. "
            "Install with: brew install ffmpeg (macOS) or sudo apt install ffmpeg (Linux)"
        )
    if not config.DENO_AVAILABLE:
        logger.warning(
            "deno not found! YouTube extraction may fail or have missing formats. "
            "Install with: brew install deno (macOS) or curl -fsSL https://deno.land/install.sh | sh (Linux)"
        )
    yield
    # Signal SSE listeners to stop on shutdown
    download_service.shutting_down = True


app = FastAPI(title="Video Library", lifespan=lifespan)

app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(downloads.router, prefix="/api/downloads", tags=["downloads"])
app.include_router(system.router, prefix="/api/system", tags=["system"])

static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=str(templates_dir))


@app.get("/")
async def index(request: Request):
    theme = get_theme(config.THEME)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "theme": theme,
    })
