from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Include routers
from app.api.routes import auth, users
from app.core.config import settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Configure logging on startup
    setup_logging()

    # Startup: could check db connection here
    yield
    # Shutdown: clean up resources


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to Backcast EVS API"}


app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
