"""
Video manager service
"""
import logging
import threading
import requests
from flask import Flask
from timeloop import Timeloop
from datetime import timedelta
from server.interfaces.video_capture_interface import VideoCaptureInterface
from server.common import ServerCameraException, ErrorCode

video_manager_timeloop = Timeloop()
POST_TIMEOUT_IN_SECS = 5

logger = logging.getLogger(__name__)


class VideoManager:
    """Service class for video manager"""

    video_capture_interface: VideoCaptureInterface
    stream_duration_in_secs: int
    orchestrator_register_service: str
    post_period_in_secs: int

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize VideoManager"""
        if app is not None:
            logger.info("initializing the VideoManager")
            self.stream_duration_in_secs = app.config["VIDEO_STREAM_DURATION_IN_SECS"]
            self.orchestrator_register_service_url = app.config["ORCHESTRATOR_REGISTER_SERVICE_URL"]
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
            logger.info(f"Posting service to orchestrator")

            data = {
                "_id": 2,
                "url": "TEST_URL"
            }
            self.post_to_orchestrator_in_dedicated_thread(
                url=self.orchestrator_register_service_url,
                data=data,
            )


        video_manager_timeloop.start(block=False)

    def get_video_stream(self):
        """Get camera video stream"""

        if self.video_capture_interface is None:
            logger.error("Error in camera, check connection and restart service")
            raise ServerCameraException(ErrorCode.CAMERA_ERROR)

        return self.video_capture_interface.get_video_stream(
            duration_in_secs=self.stream_duration_in_secs
        )


    def http_post(self, url: str, data: dict, timeout: int = POST_TIMEOUT_IN_SECS):
        """HTTP Post"""
        try:
            server_response = requests.post(
                url,
                data=(data),
                headers={"Content-Type": "application/json"},
                timeout=timeout,
            )
            logger.info(f"Server response: {server_response.text}")
        except Exception:
            logger.error(f"Error when posting to rpi cloud")


    def post_to_orchestrator_in_dedicated_thread(
        self, url: str, data: dict, timeout: int = POST_TIMEOUT_IN_SECS
    ):
        """HTTP Post in dedicated thread"""

        post_thread = threading.Thread(
            target=self.http_post,
            args=[url, data, timeout],
            name="RegistrateHttpPost",
        )
        post_thread.start()


video_manager_service: VideoManager = VideoManager()
""" VideoManager  service singleton"""
