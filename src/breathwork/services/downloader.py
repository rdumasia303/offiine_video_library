from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import yt_dlp

from .. import config

logger = logging.getLogger(__name__)


class DownloadService:
    """Wraps yt-dlp for async video downloading with progress broadcasting."""

    def __init__(self) -> None:
        self.progress_listeners: dict[int, asyncio.Queue[str]] = {}
        self.shutting_down = False

    def _broadcast(self, task_id: int, data: dict[str, Any]) -> None:
        data["task_id"] = task_id
        msg = json.dumps(data)
        for queue in list(self.progress_listeners.values()):
            try:
                queue.put_nowait(msg)
            except asyncio.QueueFull:
                pass

    def _make_progress_hook(self, task_id: int):
        def hook(d: dict[str, Any]) -> None:
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                pct = downloaded / total if total else 0
                self._broadcast(
                    task_id,
                    {
                        "progress": round(pct, 3),
                        "status": "downloading",
                        "downloaded": downloaded,
                        "total": total,
                    },
                )
            elif d["status"] == "finished":
                self._broadcast(task_id, {"progress": 1.0, "status": "processing"})

        return hook

    def _download_sync(self, task_id: int, url: str) -> dict[str, Any]:
        """Synchronous download — run via asyncio.to_thread."""
        ydl_opts = {
            "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
            "merge_output_format": "mp4",
            "outtmpl": str(config.VIDEOS_DIR / "%(title)s [%(id)s].%(ext)s"),
            "writethumbnail": True,
            "no_playlist": True,
            "progress_hooks": [self._make_progress_hook(task_id)],
            "postprocessors": [
                {
                    "key": "FFmpegThumbnailsConvertor",
                    "format": "jpg",
                }
            ],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return info  # type: ignore[return-value]

    async def download(self, task_id: int, url: str) -> dict[str, Any]:
        """Download a video asynchronously."""
        return await asyncio.to_thread(self._download_sync, task_id, url)

    def add_listener(self) -> tuple[int, asyncio.Queue[str]]:
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=100)
        lid = id(queue)
        self.progress_listeners[lid] = queue
        return lid, queue

    def remove_listener(self, lid: int) -> None:
        self.progress_listeners.pop(lid, None)


download_service = DownloadService()
