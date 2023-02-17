"""
Video capture interface service
"""
import logging
import threading
import cv2
from datetime import datetime, timedelta
from flask import Response

PICTURE_RATIO = 0.8

logger = logging.getLogger(__name__)


class VideoCaptureInterface(threading.Thread):
    """Service class for video manager interface management"""

    fps: int
    capture: cv2.VideoCapture

    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        logger.info("Video manager interface started")

    def gen_frames(self, duration_in_secs: int):
        logger.info("Streaming...")
        estimated_end = datetime.now() + timedelta(seconds=duration_in_secs)
        now = datetime.now()
        while now < estimated_end:
            success, frame = self.capture.read()  # read the camera frame
            if not success:
                logger.error("Error in video capture")
                continue
            else:
                frame = cv2.resize(
                    frame, None, fx=PICTURE_RATIO, fy=PICTURE_RATIO, interpolation=cv2.INTER_AREA
                )
                ret, buffer = cv2.imencode(".jpg", frame)
                if not ret:
                    logger.error("Error in image encode")
                    continue
                frame = buffer.tobytes()
                yield (
                    b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )  # concat frame one by one and show result
            now = datetime.now()
        logger.info("Stream finished")

    def get_video_stream(self, duration_in_secs: int):
        return Response(
            self.gen_frames(duration_in_secs), mimetype="multipart/x-mixed-replace; boundary=frame"
        )
