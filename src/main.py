from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
from src.config.database import sessionmanager
from src.config.cache import redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager
    """
    await redis_manager.connect()
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()
    await redis_manager.close()


app = FastAPI(
    title=settings.SERVICE_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {"message": "Welcome to User-service", "status": "active"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
