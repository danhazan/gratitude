from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from app.api.v1 import api_router
from app.core.database import engine, Base, TEST_DATABASE_URL, test_engine
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Grateful API...")
    
    # Use test database if TESTING environment variable is set
    if os.getenv("TESTING"):
        logger.info("Using test database")
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down Grateful API...")

app = FastAPI(
    title="Grateful API",
    description="A modern API for the Grateful social platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Grateful API", 
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "grateful-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 