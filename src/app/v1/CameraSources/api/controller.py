from fastapi import BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from typing import AsyncGenerator
import cv2, threading, os, asyncio
from src.app.v1.CameraSources.services.ConvertRTSP import run_ffmpeg
from typing import Optional, Union

HLS_DIR = os.getenv("HLS_DIR", "./hls")
pcs = set()

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

class Camera:
    """
    A class to handle video capture from a camera.
    """

    def __init__(self, url: Optional[Union[str, int]] = 0) -> None:
        """
        Initialize the camera.

        :param url: Camera index or URL.
        """
        self.cap = cv2.VideoCapture(url)
        self.lock = threading.Lock()

    def get_frame(self) -> bytes:
        """
        Capture a frame from the camera.

        :return: JPEG encoded image bytes.
        """
        with self.lock:
            ret, frame = self.cap.read()
            if not ret:
                return b''

            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                return b''

            return jpeg.tobytes()

    def release(self) -> None:
        """
        Release the camera resource.
        """
        with self.lock:
            if self.cap.isOpened():
                self.cap.release()


async def gen_frames() -> AsyncGenerator[bytes, None]:
    camera = Camera(0)
    try:
        while True:
            frame = camera.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                print("No frame received from camera.")
                break
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        print("Frame generation cancelled.")
    except Exception as e:
        print(f"Error in frame generation: {e}")
    finally:
        camera.release()
        print("Frame generator exited.")


async def videoFeedWebcam() -> StreamingResponse:
    """
    Video streaming route.

    :return: StreamingResponse with multipart JPEG frames.
    """
    return StreamingResponse(
        gen_frames(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )