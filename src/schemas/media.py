from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MediaBase(BaseModel):
    media_type: str
    file_path: str

class MediaCreate(MediaBase):
    post_id: int

class MediaResponse(MediaBase):
    id: int
    user_id: int
    post_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True 