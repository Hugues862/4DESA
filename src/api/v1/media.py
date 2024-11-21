from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
import aiofiles
import os
from src.core.database import get_db
from src.core.config import get_settings
from src.services.auth_service import get_current_user
from src.models.media import Media

router = APIRouter()
settings = get_settings()

@router.post("/upload")
async def upload_media(
    file: UploadFile,
    post_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if file.content_type not in settings.ALLOWED_MEDIA_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed")

    file_path = f"{settings.MEDIA_ROOT}/{file.filename}"
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    db_media = Media(
        file_path=file_path,
        media_type=file.content_type,
        post_id=post_id,
        user_id=current_user.id
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    
    return {"filename": file.filename, "media_id": db_media.id} 