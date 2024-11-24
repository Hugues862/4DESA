from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from src.core.database import get_db
from src.models.post import Post
from src.models.media import Media
from src.schemas.post import PostCreate, PostResponse, PostUpdate
from src.services.auth_service import get_current_user

router = APIRouter()

@router.post("/", response_model=PostResponse)
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

@router.get("/", response_model=List[PostResponse])
async def get_posts(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Post)
    
    # Apply search filter if search parameter is provided
    if search:
        query = query.filter(
            or_(
                Post.title.ilike(f"%{search}%"),
                Post.content.ilike(f"%{search}%")
            )
        )
    
    # Apply visibility filter
    query = query.filter(
        or_(
            Post.is_public == True,
            Post.user_id == current_user.id
        )
    )
    
    # Apply pagination
    posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts

@router.get("/{post_id}", response_model=PostResponse)
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

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    
    for field, value in post_update.dict(exclude_unset=True).items():
        setattr(db_post, field, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    db.delete(db_post)
    db.commit()
    return None

@router.post("/{post_id}/media/{media_id}")
async def assign_media_to_post(
    post_id: int,
    media_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if post exists and user owns it
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this post")

    # Check if media exists and user owns it
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if media.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to use this media")

    # Assign media to post
    media.post_id = post_id
    db.commit()
    db.refresh(media)

    return {"message": "Media assigned to post successfully"}


@router.get("/user/{user_id}", response_model=List[PostResponse])
async def get_user_posts(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get posts for a specific user, respecting visibility
    posts = db.query(Post).filter(
        Post.user_id == user_id
    ).filter(
        or_(
            Post.is_public == True,
            Post.user_id == current_user.id
        )
    ).offset(skip).limit(limit).all()

    return posts