from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings
from app.core.logger import logger
from app.core.cache import prewarm_models
from app.database.database import Base, engine

# Import Middlewares
from app.middlewares.exception import GlobalExceptionMiddleware
from app.middlewares.logging import RequestLoggingMiddleware

# Import Routers
from app.routers import auth, resume, job_description, analysis, report, chat, interview

# Auto-create database tables on startup (Postgres or SQLite fallback)
logger.info("Initializing database schemas auto-creation...")
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("FastAPI Application starting up...")
    prewarm_models()
    yield
    # Shutdown actions
    logger.info("FastAPI Application shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Enterprise-grade AI Resume Analyzer API built with FastAPI, spaCy, and Gemini.",
    lifespan=lifespan
)

# Mount Middlewares
app.add_middleware(GlobalExceptionMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# CORS Configuration
# Adjust origins in production as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Versioned API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(resume.router, prefix=settings.API_V1_STR)
app.include_router(job_description.router, prefix=settings.API_V1_STR)
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(report.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(interview.router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def health_check():
    """Simple status check endpoint."""
    return {
        "success": True,
        "message": "API service is healthy",
        "data": {
            "status": "online",
            "model": settings.MODEL_NAME
        }
    }
