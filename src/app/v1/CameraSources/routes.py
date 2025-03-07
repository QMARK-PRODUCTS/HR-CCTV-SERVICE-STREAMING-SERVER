from fastapi import APIRouter
from src.app.v1.CameraSources.api.controller import *

router = APIRouter()

routes = [
    {
        "route": "/convert/",
        "method": ["POST"],
        "handler": convert_rtsp_to_hls,
        "name": "Convert RTSP to HLS"
    },
    {
        "route": "/hls/{stream_id}/{segment_name}",
        "method": ["GET"],
        "handler": get_hls_playlist,
        "name": "Get HLS Playlist"
    },
    {
        "route": "/webcam-video",
        "method": ["GET"],
        "handler": videoFeedWebcam,
        "name": "Get Webcam Video"
    }
]

for route in routes:
    router.add_api_route(route["route"], route["handler"], methods=route["method"], name=route["name"])
