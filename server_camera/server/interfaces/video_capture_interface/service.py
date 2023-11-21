"""
Video capture interface service
"""
import logging
import threading
from picamera2 import Picamera2
import io
import time
from datetime import datetime, timedelta
from flask import Response

PICTURE_RATIO = 0.8

logger = logging.getLogger(__name__)


class VideoCaptureInterface(threading.Thread):
    """Service class for video manager interface management"""

    fps: int
    picam: Picamera2

    def __init__(self):
        self.picam = Picamera2()
        camera_config = self.picam.create_preview_configuration()
        self.picam.configure(camera_config)
        self.picam.start()
        time.sleep(2)
        logger.info("Video manager interface started")

    def gen_frames(self, duration_in_secs: int):
        logger.info("Streaming...")
        estimated_end = datetime.now() + timedelta(seconds=duration_in_secs)
        now = datetime.now()
        while now < estimated_end:
            # TODO:  Try exception
            # frame = self.picam.capture_array() # read the camera frame
            stream = io.BytesIO()
            self.picam.capture_file(stream, format="jpeg")  # this is the laggy bit
            stream.seek(0)  # goes to start of buffer
            frame = stream.read()
            stream.truncate()  # cleans up buffer memory

            # frame = cv2.resize(
            #     frame,
            #     None,
            #     fx=PICTURE_RATIO,
            #     fy=PICTURE_RATIO,
            #     interpolation=cv2.INTER_AREA,
            # )
            # ret, buffer = cv2.imencode(".jpg", frame)
            # if not ret:
            #     logger.error("Error in image encode")
            #     continue
            # frame = buffer.tobytes()
            yield (
                b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )  # concat frame one by one and show result
            now = datetime.now()
        logger.info("Stream finished")

    def get_video_stream(self, duration_in_secs: int):
        return Response(
            self.gen_frames(duration_in_secs),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
