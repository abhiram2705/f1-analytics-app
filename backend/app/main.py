import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.database import create_all_tables
from app.routers import races, fastest_laps, tyres, pit_stops, standings, ingest

app = FastAPI(
    title="F1 Analytics API",
    description="FastF1-powered Formula 1 race analytics backend",
    version="1.0.0",
)

# CORS — allow the Vite dev server
cors_origin = os.getenv("CORS_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[cors_origin, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(races.router)
app.include_router(fastest_laps.router)
app.include_router(tyres.router)
app.include_router(pit_stops.router)
app.include_router(standings.router)
app.include_router(ingest.router)


@app.on_event("startup")
def startup_event():
    """Create all DB tables on startup if they don't exist."""
    create_all_tables()


@app.get("/health")
def health():
    return {"status": "ok", "service": "f1-analytics-api"}


@app.get("/")
def root():
    return {
        "message": "F1 Analytics API",
        "docs": "/docs",
        "redoc": "/redoc",
    }
