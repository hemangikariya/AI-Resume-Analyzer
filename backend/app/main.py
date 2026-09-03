from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings
from app.core.logger import logger
from app.database.database import Base, engine

# Import Middlewares
from app.middlewares.exception import GlobalExceptionMiddleware
from app.middlewares.logging import RequestLoggingMiddleware

# Import Routers
from app.routers import auth, resume, job_description, analysis, report, chat, interview

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions: initialize database schemas safely
    logger.info("FastAPI Application starting up...")
    try:
        logger.info("Initializing database schemas auto-creation...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas verified.")
    except Exception as e:
        logger.warning(f"Database schema auto-creation encountered non-fatal error: {e}")

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
# Production Vercel origins & local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
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
