"""
Video manager service
"""
import logging
from flask import Flask
from timeloop import Timeloop
from server.interfaces.video_capture_interface import VideoCaptureInterface
from server.common import ServerCameraException, ErrorCode

last_frame_test_timeloop = Timeloop()

logger = logging.getLogger(__name__)


class VideoManager:
    """Service class for video manager"""

    video_capture_interface: VideoCaptureInterface

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize VideoManager"""
        if app is not None:
            logger.info("initializing the VideoManager")
            self.stream_duration_in_secs = app.config["VIDEO_STREAM_DURATION_IN_SECS"]
            self.video_capture_interface = VideoCaptureInterface()

    def get_video_stream(self):
        """Get camera video stream"""

        if self.video_capture_interface is None:
            logger.error("Error in camera, check connection and restart service")
            raise ServerCameraException(ErrorCode.CAMERA_ERROR)

        return self.video_capture_interface.get_video_stream(
            duration_in_secs=self.stream_duration_in_secs
        )


video_manager_service: VideoManager = VideoManager()
""" VideoManager  service singleton"""
