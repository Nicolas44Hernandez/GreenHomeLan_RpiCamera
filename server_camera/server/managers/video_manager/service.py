"""
Video manager service
"""
import logging
import threading
import requests
import socket
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
    cam_id: int
    url_path: str
    video_server_url: str

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
            self.cam_id = app.config["CAM_ID"]
            self.url_path = ":5000/video_stream"
            self.video_server_url = self.get_video_server_address()

            # Schedule video manager tasks
            self.schedule_tasks()


    def get_video_server_address(self):
        """ Return video server address"""
        # Get Orchestrator ip address
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("192.168.1.122", 80))
            ip_addr = s.getsockname()[0]
            base_url = f"http://{ip_addr}{self.url_path}"
            s.close()
            return base_url
        except:
            logger.error("Error retreiving IP")
            return None


    def schedule_tasks(self):
        """Schedule the video manager tasks"""

        logger.info(f"Schedule tasks")

        # Start wifi status polling service
        @video_manager_timeloop.job(
            interval=timedelta(seconds=self.post_period_in_secs)
        )
        def post_service_to_orchestrator():
            # Register service to orchestrator
            logger.info(f"Posting service to orchestrator in: {self.orchestrator_register_service_url}")

            data = {
                "_id": self.cam_id,
                "url": self.video_server_url,
            }
            self.post_to_orchestrator_in_dedicated_thread(
                url=self.orchestrator_register_service_url,
                data=data,
            )


        video_manager_timeloop.start(block=False)

    def get_video_stream(self):
        """Get camera video stream"""

        logger.info("Getting video stream...")

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
                json=data,
                timeout=timeout,
            )
            logger.info(f"Server response: {server_response.text}")
            #TODO: what to do with the key
        except Exception as e:
            logger.error(f"Error when posting to orchestrator")


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
