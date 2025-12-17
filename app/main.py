from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, close_db, init_chroma, close_chroma
from app.api.middleware import LoggingMiddleware, RateLimitMiddleware
from app.api.routes import health, recommend
from app.utils.logger import get_logger
from scripts.initailize_vector_store import initialize_vector_store
logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    logger.info("Starting SHL Assessment Recommendation System...")
    
    try:
        logger.info("Initializing databases...")
        init_db()
        init_chroma()
        
        await initialize_vector_store()
        
        logger.info("Startup complete!")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield
    
    logger.info("Shutting down...")
    
    try:
        await close_chroma()
        await close_db()
        
        logger.info("Shutdown complete")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


app = FastAPI(
    title="SHL Assessment Recommendation System",
    description="API for recommending SHL assessments based on job descriptions and queries",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)
app.include_router(health.router)
app.include_router(recommend.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SHL Assessment Recommendation System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        workers=settings.API_WORKERS
    )