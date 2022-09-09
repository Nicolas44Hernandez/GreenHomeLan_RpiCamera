"""
Video manager service
"""
import logging
from flask import Flask
from timeloop import Timeloop
from server.interfaces.video_capture_interface import VideoCaptureInterface

last_frame_test_timeloop = Timeloop()

logger = logging.getLogger(__name__)


class VideoManager:
    """Service class for video manager"""

    # attributes
    video_capture_interface: VideoCaptureInterface
    counter: int

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize VideoManager"""
        if app is not None:
            logger.info("initializing the VideoManager")
            self.video_capture_interface = VideoCaptureInterface()
            self.capture_running = True

    def set_video_capture_running_status(self, running: bool):
        """Set the video capture status (runnning / waiting)"""

        logger.info(f"Setting video capture running to {running}")
        self.video_capture_interface.running = running


    def get_last_captured_frame(self):
        """Retreive last captured frame"""

        return self.video_capture_interface.get_last_frame()

video_manager_service: VideoManager = VideoManager()
""" VideoManager  service singleton"""
