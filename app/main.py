import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()
    
    # Initialize FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        description="API for detecting bot behavior using multiple signals",
        version=settings.APP_VERSION,
        debug=settings.DEBUG
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify your frontend domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(api_router)
    
    return app

app = create_application()

@app.on_event("startup")
async def startup_event():
    """Application startup events"""
    logger.info("Starting Bot Detection API")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown events"""
    logger.info("Shutting down Bot Detection API")

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=settings.DEBUG)