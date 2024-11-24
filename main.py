from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from src.core.config import get_settings
from src.api.v1 import auth, post, media
from src.core.database import Base, engine

settings = get_settings()

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A flexible social media platform for content creators",
    version=settings.VERSION,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",  # API server
        "http://localhost:3000",  # Frontend (if different)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(
    auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"]
)
app.include_router(post.router, prefix=f"{settings.API_V1_STR}/posts", tags=["Posts"])
app.include_router(media.router, prefix=f"{settings.API_V1_STR}/media", tags=["Media"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
