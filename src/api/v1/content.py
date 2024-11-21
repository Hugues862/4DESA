from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.models.content import Post
from src.schemas.content import PostCreate, PostResponse
from src.services.auth_service import get_current_user

router = APIRouter()

@router.post("/posts", response_model=PostResponse)
async def create_post(
    post: PostCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_post = Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id,
        is_public=post.is_public
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not post.is_public and post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this post")
    return post 