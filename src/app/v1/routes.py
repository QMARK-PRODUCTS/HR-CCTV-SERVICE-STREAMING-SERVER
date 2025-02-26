from fastapi import APIRouter
from src.app.v1.CameraSources.routes import router as CameraSourcesRouter

router = APIRouter()

router.include_router(CameraSourcesRouter, prefix="/camera-sources", tags=["Camera Sources"])