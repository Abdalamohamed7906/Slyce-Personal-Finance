"""Entry point. Run with:  uvicorn app.main:app --reload"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import auth, paychecks, savings, stocks

# Creates the tables on first run. (Later you can switch to Alembic migrations.)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Slyce", description="Paycheck splitting with the 50/30/20 rule")

app.include_router(auth.router)
app.include_router(paychecks.router)
app.include_router(savings.router)
app.include_router(stocks.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


# Serve the frontend at http://localhost:8000/  (mounted last so API routes win)
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
