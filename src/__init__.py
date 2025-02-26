from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from contextlib import asynccontextmanager
from src.database.db import initDB
from src.app.v1.routes import router as v1Router
import os, sys
from dotenv import load_dotenv

load_dotenv()
hls_dir = os.getenv("HLS_DIR")

if not hls_dir:
    raise RuntimeError("HLS_DIR is not set. Please check your .env file.")

sys.dont_write_bytecode = True

@asynccontextmanager
async def lifespan(app : FastAPI):
    initDB()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="CCTV Streaming Service",
    version="v1",
    description="This is the backend service for the CCTV project.",    
    )

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


os.makedirs(hls_dir, exist_ok=True)

app.mount("/hls", StaticFiles(directory=hls_dir), name="hls")

app.include_router(v1Router, prefix="/api/v1")