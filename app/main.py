from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.error_handlers import register_error_handlers
from app.models import Payment, Spot, Ticket
from app.models.seed import seed_initial_spots
from app.routers import pricing, spots, stats, tickets


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_spots(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    lifespan=lifespan,
)

register_error_handlers(app)

app.include_router(spots.router)
app.include_router(tickets.router)
app.include_router(pricing.router)
app.include_router(stats.router)

static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
