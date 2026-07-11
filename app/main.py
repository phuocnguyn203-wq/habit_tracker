from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database.database import init_db
from app.routers import habits, habit_records, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(habits.router)
app.include_router(habit_records.router)
app.include_router(users.router)

STATIC_DIR = Path(__file__).resolve().parent / 'static'
app.mount('/', StaticFiles(directory=STATIC_DIR, html=True), name='static')