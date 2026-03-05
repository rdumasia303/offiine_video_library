from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .. import config
from ..database import get_session
from ..models import DownloadTask, Video
from ..schemas import DownloadRequest, DownloadTaskOut
from ..services.downloader import download_service

logger = logging.getLogger(__name__)
router = APIRouter()


async def _run_download(task_id: int, url: str) -> None:
    """Background task: run yt-dlp and update DB on completion."""
    from ..database import async_session

    async with async_session() as session:
        try:
            # Mark as downloading
            await session.execute(
                update(DownloadTask)
                .where(DownloadTask.id == task_id)
                .values(status="downloading", updated_at=datetime.now(timezone.utc))
            )
            await session.commit()

            info = await download_service.download(task_id, url)

            video_id = info["id"]
            ext = info.get("ext", "mp4")

            # Find the downloaded file by scanning for the video ID in the name.
            # We can't use glob because titles may contain glob-special chars
            # like brackets. yt-dlp writes "Title [videoID].ext".
            filename = None
            filepath = None
            vid_tag = f"[{video_id}]"
            for candidate in config.VIDEOS_DIR.iterdir():
                if candidate.is_file() and vid_tag in candidate.name and candidate.suffix == f".{ext}":
                    filepath = candidate
                    filename = candidate.name
                    break
            if not filename:
                # Fallback: plain ID naming (older downloads)
                fallback = config.VIDEOS_DIR / f"{video_id}.{ext}"
                if fallback.exists():
                    filepath = fallback
                    filename = fallback.name
            if not filename:
                raise RuntimeError(f"Downloaded file not found for {video_id}")

            file_size = filepath.stat().st_size

            # Find thumbnail — same scanning approach
            thumb_path = None
            for suffix in [".jpg", ".webp", ".png"]:
                for candidate in config.VIDEOS_DIR.iterdir():
                    if candidate.is_file() and vid_tag in candidate.name and candidate.suffix == suffix:
                        dest = config.THUMBNAILS_DIR / f"{video_id}{suffix}"
                        candidate.rename(dest)
                        thumb_path = f"{video_id}{suffix}"
                        break
                if thumb_path:
                    break
                # Fallback: old ID-only naming
                old = config.VIDEOS_DIR / f"{video_id}{suffix}"
                if old.exists():
                    dest = config.THUMBNAILS_DIR / f"{video_id}{suffix}"
                    old.rename(dest)
                    thumb_path = f"{video_id}{suffix}"
                    break

            # Determine resolution
            resolution = None
            if info.get("height"):
                resolution = f"{info['height']}p"

            # Create or update video record
            existing = await session.get(Video, video_id)
            if existing:
                existing.title = info.get("title", "Untitled")
                existing.file_path = filename
                existing.file_size = file_size
            else:
                video = Video(
                    id=video_id,
                    title=info.get("title", "Untitled"),
                    channel=info.get("uploader") or info.get("channel"),
                    duration=info.get("duration"),
                    description=info.get("description", ""),
                    thumbnail=thumb_path,
                    file_path=filename,
                    file_size=file_size,
                    format=ext,
                    resolution=resolution,
                    url=url,
                )
                session.add(video)

            # Update download task
            await session.execute(
                update(DownloadTask)
                .where(DownloadTask.id == task_id)
                .values(
                    status="completed",
                    progress=1.0,
                    video_id=video_id,
                    title=info.get("title", ""),
                    updated_at=datetime.now(timezone.utc),
                )
            )
            await session.commit()

            download_service._broadcast(
                task_id,
                {"status": "completed", "progress": 1.0, "video_id": video_id},
            )

        except Exception as e:
            logger.exception("Download failed for task %s", task_id)
            await session.execute(
                update(DownloadTask)
                .where(DownloadTask.id == task_id)
                .values(
                    status="failed",
                    error_message=str(e),
                    updated_at=datetime.now(timezone.utc),
                )
            )
            await session.commit()

            download_service._broadcast(
                task_id,
                {"status": "failed", "error": str(e)},
            )


@router.post("", response_model=DownloadTaskOut)
async def start_download(
    req: DownloadRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    task = DownloadTask(url=req.url, status="pending")
    session.add(task)
    await session.commit()
    await session.refresh(task)

    background_tasks.add_task(_run_download, task.id, req.url)
    return task


@router.get("", response_model=list[DownloadTaskOut])
async def list_downloads(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(DownloadTask).order_by(DownloadTask.created_at.desc()).limit(50)
    )
    return result.scalars().all()


@router.get("/progress")
async def download_progress():
    lid, queue = download_service.add_listener()

    async def event_stream():
        try:
            while not download_service.shutting_down:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        except (asyncio.CancelledError, GeneratorExit):
            pass
        finally:
            download_service.remove_listener(lid)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.delete("/{task_id}")
async def cancel_download(
    task_id: int, session: AsyncSession = Depends(get_session)
):
    task = await session.get(DownloadTask, task_id)
    if not task:
        raise HTTPException(404, "Download task not found")
    if task.status in ("pending", "downloading"):
        task.status = "cancelled"
        await session.commit()
    return {"status": "ok"}
