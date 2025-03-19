import os
import logging
from fastapi import FastAPI, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .api import router
from .database import init_db, DatabaseOperations
from .processor import VideoProcessor
from config.settings import CONFIG, setup_logging

# Set up logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Video Analysis and Metadata Management",
    description="API for analyzing videos, extracting subtitles, recognizing movie names, and fetching metadata",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_db_client():
    try:
        # Initialize database
        db_engine = init_db(CONFIG["database_url"])
        app.state.db_operations = DatabaseOperations(db_engine)
        
        # Initialize video processor
        app.state.video_processor = VideoProcessor()
        
        # Create output and upload directories if they don't exist
        os.makedirs(CONFIG["output_dir"], exist_ok=True)
        os.makedirs("uploads", exist_ok=True)
        
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

# Dependency to get database operations from app state
def get_db_operations(request: Request):
    return request.app.state.db_operations

# Dependency to get video processor from app state
def get_video_processor(request: Request):
    return request.app.state.video_processor

# Update API router dependencies
app.include_router(
    router,
    prefix="/api",
    dependencies=[
        Depends(get_db_operations),
        Depends(get_video_processor)
    ]
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=CONFIG["api_host"],
        port=CONFIG["api_port"],
        reload=True
    ) 