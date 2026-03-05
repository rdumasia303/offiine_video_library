from datetime import datetime

from pydantic import BaseModel


class VideoOut(BaseModel):
    id: str
    title: str
    channel: str | None = None
    duration: int | None = None
    description: str | None = None
    thumbnail: str | None = None
    file_path: str
    file_size: int | None = None
    format: str | None = None
    resolution: str | None = None
    url: str
    notes: str = ""
    tags: str = ""
    is_favorite: bool = False
    last_watched: datetime | None = None
    watch_count: int = 0
    downloaded_at: datetime | None = None

    model_config = {"from_attributes": True}


class VideoUpdate(BaseModel):
    notes: str | None = None
    tags: str | None = None
    is_favorite: bool | None = None


class DownloadRequest(BaseModel):
    url: str


class DownloadTaskOut(BaseModel):
    id: int
    url: str
    status: str
    progress: float
    error_message: str | None = None
    video_id: str | None = None
    title: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class RevealRequest(BaseModel):
    video_id: str


class SystemInfo(BaseModel):
    local_ips: list[str]
    port: int
    video_count: int
    total_size_mb: float
    theme: str = "breathwork"
