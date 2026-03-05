from __future__ import annotations

import mimetypes
from datetime import datetime, timezone
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import config
from ..database import get_session
from ..models import Video
from ..schemas import VideoOut, VideoUpdate

router = APIRouter()


def _parse_range(range_header: str, file_size: int) -> tuple[int, int]:
    """Parse a Range header like 'bytes=0-1023' into (start, end)."""
    range_spec = range_header.replace("bytes=", "")
    parts = range_spec.split("-")
    start = int(parts[0]) if parts[0] else 0
    end = int(parts[1]) if parts[1] else file_size - 1
    end = min(end, file_size - 1)
    return start, end


@router.get("", response_model=list[VideoOut])
async def list_videos(
    search: str | None = None,
    tag: str | None = None,
    favorite: bool | None = None,
    sort: str = "downloaded_at",
    session: AsyncSession = Depends(get_session),
):
    query = select(Video)

    if search:
        pattern = f"%{search}%"
        query = query.where(
            Video.title.ilike(pattern) | Video.notes.ilike(pattern)
        )
    if tag:
        query = query.where(Video.tags.ilike(f"%{tag}%"))
    if favorite is not None:
        query = query.where(Video.is_favorite == favorite)

    sort_col = getattr(Video, sort, Video.downloaded_at)
    query = query.order_by(sort_col.desc())

    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{video_id}", response_model=VideoOut)
async def get_video(video_id: str, session: AsyncSession = Depends(get_session)):
    video = await session.get(Video, video_id)
    if not video:
        raise HTTPException(404, "Video not found")
    return video


@router.patch("/{video_id}", response_model=VideoOut)
async def update_video(
    video_id: str,
    data: VideoUpdate,
    session: AsyncSession = Depends(get_session),
):
    video = await session.get(Video, video_id)
    if not video:
        raise HTTPException(404, "Video not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(video, key, val)
    video.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(video)
    return video


@router.delete("/{video_id}")
async def delete_video(video_id: str, session: AsyncSession = Depends(get_session)):
    video = await session.get(Video, video_id)
    if not video:
        raise HTTPException(404, "Video not found")

    # Delete video file
    video_file = config.VIDEOS_DIR / video.file_path
    if video_file.exists():
        video_file.unlink()

    # Delete thumbnail
    if video.thumbnail:
        thumb_file = config.THUMBNAILS_DIR / video.thumbnail
        if thumb_file.exists():
            thumb_file.unlink()

    await session.delete(video)
    await session.commit()
    return {"status": "ok"}


@router.get("/{video_id}/stream")
async def stream_video(video_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    video = await session.get(Video, video_id)
    if not video:
        raise HTTPException(404, "Video not found")

    file_path = config.VIDEOS_DIR / video.file_path
    if not file_path.exists():
        raise HTTPException(404, "Video file missing from disk")

    file_size = file_path.stat().st_size
    content_type = mimetypes.guess_type(str(file_path))[0] or "video/mp4"

    range_header = request.headers.get("range")
    if range_header:
        start, end = _parse_range(range_header, file_size)
        content_length = end - start + 1

        async def ranged_stream():
            async with aiofiles.open(file_path, "rb") as f:
                await f.seek(start)
                remaining = content_length
                while remaining > 0:
                    chunk_size = min(65536, remaining)
                    chunk = await f.read(chunk_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        return StreamingResponse(
            ranged_stream(),
            status_code=206,
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
                "Content-Type": content_type,
            },
        )

    return FileResponse(file_path, media_type=content_type)


@router.get("/{video_id}/download")
async def download_video(video_id: str, session: AsyncSession = Depends(get_session)):
    """Serve video as a downloadable attachment (for saving to phone)."""
    video = await session.get(Video, video_id)
    if not video:
        raise HTTPException(404, "Video not found")

    file_path = config.VIDEOS_DIR / video.file_path
    if not file_path.exists():
        raise HTTPException(404, "Video file missing from disk")

    # Clean the title for use as a filename on any device
    safe_title = video.title
    for ch in r'\/:"*?<>|':
        safe_title = safe_title.replace(ch, "-")
    safe_title = safe_title.strip(". ")
    download_name = f"{safe_title}.mp4"

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=download_name,
        headers={
            "Cache-Control": "no-cache",
        },
    )


@router.get("/{video_id}/thumbnail")
async def get_thumbnail(video_id: str, session: AsyncSession = Depends(get_session)):
    video = await session.get(Video, video_id)
    if not video or not video.thumbnail:
        raise HTTPException(404, "Thumbnail not found")

    thumb_path = config.THUMBNAILS_DIR / video.thumbnail
    if not thumb_path.exists():
        raise HTTPException(404, "Thumbnail file missing")

    return FileResponse(thumb_path)


@router.post("/{video_id}/watch")
async def mark_watched(video_id: str, session: AsyncSession = Depends(get_session)):
    video = await session.get(Video, video_id)
    if not video:
        raise HTTPException(404, "Video not found")
    video.watch_count += 1
    video.last_watched = datetime.now(timezone.utc)
    await session.commit()
    return {"status": "ok", "watch_count": video.watch_count}
