"""FastAPI application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from .routes import router
from .dependencies import reset_shared_state


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    reset_shared_state()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Alethic Kernel API",
        description="Domain-agnostic AI governance kernel",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(router)
    return app
