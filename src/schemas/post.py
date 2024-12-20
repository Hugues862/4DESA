from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .media import MediaResponse

class PostBase(BaseModel):
    title: str
    content: str
    is_public: bool = True

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_public: Optional[bool] = None

class PostResponse(PostBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    media: List[MediaResponse] = []

    class Config:
        from_attributes = True 