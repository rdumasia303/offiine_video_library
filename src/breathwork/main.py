from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import config
from .database import init_db
from .routers import downloads, system, videos
from .services.downloader import download_service
from .themes import get_theme


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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
