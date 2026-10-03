from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from floranova.config import settings
from floranova.database import init_db
from floranova.api.v1 import api_router
from floranova.web.routes import web_router

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables are created
    await init_db()
    yield
    # Shutdown cleanups if needed


app = FastAPI(
    title=settings.APP_TITLE,
    description="Artisan Floral Operations & E-Commerce Platform with Jalali Scheduling, Perishable Stock Tracking, and Atelier Admin Panel",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware for headless or external integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Mount Routers
app.include_router(api_router)
app.include_router(web_router)


def main():
    import uvicorn
    uvicorn.run("floranova.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
