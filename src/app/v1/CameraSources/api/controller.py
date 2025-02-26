from fastapi import BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse
from src.app.v1.CameraSources.services.ConvertRTSP import run_ffmpeg
import os

HLS_DIR = os.getenv("HLS_DIR", "./hls")


async def convert_rtsp_to_hls(background_tasks: BackgroundTasks, rtsp_url: str, request: Request):
    """Converts an RTSP stream to HLS format asynchronously"""

    stream_id = abs(hash(rtsp_url))  # Ensure non-negative ID
    stream_dir = os.path.join(HLS_DIR, str(stream_id))
    os.makedirs(stream_dir, exist_ok=True)

    background_tasks.add_task(run_ffmpeg, rtsp_url, stream_dir)
    
    server_url = f"{request.base_url}"

    hls_url = f"{server_url}api/v1/camera-sources/hls/{stream_id}/index.m3u8"
    
    return {"hls_url": hls_url}



async def get_hls_playlist(stream_id: str, segment_name: str):
    """ Serve individual HLS .ts segment files """
    segment_path = os.path.join(HLS_DIR, stream_id, segment_name)

    if not os.path.isfile(segment_path):
        raise HTTPException(status_code=404, detail=f"Segment {segment_name} not found")

    return FileResponse(segment_path, media_type="video/mp2t")

