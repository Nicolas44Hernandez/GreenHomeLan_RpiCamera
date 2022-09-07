"""
Video manager service
"""
import logging
from flask import Flask
import cv2



logger = logging.getLogger(__name__)


class VideoManager:
    """Service class for video manager"""

    # attributes

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize VideoManager"""
        if app is not None:
            logger.info("initializing the VideoManager")

            # Get config
            # self.polling_period_in_secs = app.config["WIFI_CONNECTION_STATUS_POLL_PERIOD_IN_SECS"]


video_manager_service: VideoManager = VideoManager()
""" VideoManager  service singleton"""
