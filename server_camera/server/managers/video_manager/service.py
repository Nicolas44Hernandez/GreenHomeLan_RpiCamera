"""
Video manager service
"""
import logging
from flask import Flask
from timeloop import Timeloop
from datetime import timedelta
from server.interfaces.video_capture_interface import VideoCaptureInterface
from server.common import ServerCameraException, ErrorCode

video_manager_timeloop = Timeloop()

logger = logging.getLogger(__name__)


class VideoManager:
    """Service class for video manager"""

    video_capture_interface: VideoCaptureInterface
    stream_duration_in_secs: int
    orchestrator_ip: str
    post_period_in_secs: int

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize VideoManager"""
        if app is not None:
            logger.info("initializing the VideoManager")
            self.stream_duration_in_secs = app.config["VIDEO_STREAM_DURATION_IN_SECS"]
            self.orchestrator_ip = app.config["ORCHESTRATOR_IP"]
            self.video_capture_interface = VideoCaptureInterface()
            self.post_period_in_secs = app.config["POST_SERVICE_TO_ORCHESTRATOR_PERIOD_IN_SECS"]

            # Schedule video manager tasks
            self.schedule_tasks()

    def schedule_tasks(self):
        """Schedule the video manager tasks"""

        logger.info(f"Schedule tasks")

        # Start wifi status polling service
        @video_manager_timeloop.job(
            interval=timedelta(seconds=self.post_period_in_secs)
        )
        def post_service_to_orchestrator():
            # Register service to orchestrator
            logger.info(f"Posting service to orchestrator WIP")

        video_manager_timeloop.start(block=False)

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
