from __future__ import annotations

import socket
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import config
from ..database import get_session
from ..models import Video
from ..schemas import RevealRequest, SystemInfo

router = APIRouter()


def _get_local_ips() -> list[str]:
    ips = []
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            addr = info[4][0]
            if not addr.startswith("127."):
                ips.append(addr)
    except Exception:
        pass

    # Fallback: connect to a known address to find the default route IP
    if not ips:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ips.append(s.getsockname()[0])
            s.close()
        except Exception:
            pass

    return list(set(ips)) or ["127.0.0.1"]


@router.post("/reveal")
async def reveal_in_finder(
    req: RevealRequest, session: AsyncSession = Depends(get_session)
):
    video = await session.get(Video, req.video_id)
    if not video:
        raise HTTPException(404, "Video not found")

    file_path = config.VIDEOS_DIR / video.file_path
    if not file_path.exists():
        raise HTTPException(404, "Video file not found on disk")

    if sys.platform == "darwin":
        subprocess.Popen(["open", "-R", str(file_path)])
    else:
        subprocess.Popen(["xdg-open", str(file_path.parent)])

    return {"status": "ok"}


@router.get("/info", response_model=SystemInfo)
async def get_system_info(session: AsyncSession = Depends(get_session)):
    # Count videos
    result = await session.execute(select(func.count(Video.id)))
    video_count = result.scalar() or 0

    # Calculate total size
    total_bytes = 0
    if config.VIDEOS_DIR.exists():
        for f in config.VIDEOS_DIR.iterdir():
            if f.is_file():
                total_bytes += f.stat().st_size

    return SystemInfo(
        local_ips=_get_local_ips(),
        port=config.PORT,
        video_count=video_count,
        total_size_mb=round(total_bytes / (1024 * 1024), 1),
        theme=config.THEME,
    )
