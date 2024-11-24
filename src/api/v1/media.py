from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.config import get_settings
from src.services.auth_service import get_current_user
from src.services.azure_storage import AzureStorageService
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

    # Check file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size too large")

    # Upload to Azure Blob Storage
    storage_service = AzureStorageService()
    file_url = await storage_service.upload_file(content, file.content_type)

    # Save media information to database
    db_media = Media(
        file_path=file_url,  # Store the Azure Blob URL instead of local path
        media_type=file.content_type,
        post_id=post_id,
        user_id=current_user.id
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    
    return {
        "media_id": db_media.id,
        "url": file_url,
        "media_type": file.content_type
    } 