import logging
import requests
from requests.exceptions import ConnectionError, InvalidURL
from flask import Flask
from server.managers.ip_discovery import IpDiscoveryService as ip_discovery_service


logger = logging.getLogger(__name__)


class CloudNotifier:
    """Manager for CloudNotifier"""

    rpi_cloud_ip: str = None
    rpi_cloud_ports: str
    rpi_cloud_video_stream_path: str

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize CloudNotifier"""
        if app is not None:
            logger.info("initializing the CloudNotifier")

            # retrieve RPI box ip
            self.rpi_cloud_ip = ip_discovery_service.get_ip_addr(mac=app.config["RPI_CLOUD_MAC"])
            self.rpi_cloud_ports = app.config["RPI_CLOUD_PORTS"]
            self.rpi_cloud_video_stream_path = app.config["RPI_CLOUD_EVENT_PATH"]

    def notify_video_stream_ready(self, stream_ready: bool, trigger: str = None):
        """Call HTTP post to notify video stream status to rpi cloud"""

        logger.info(f"Posting HTTP to notify video stream status {stream_ready} to RPI cloud")

        # Post video stream status to rpi cloud
        for port in self.rpi_cloud_ports:
            post_url = (
                f"http://{self.rpi_cloud_ip}:{port}/{self.rpi_cloud_video_stream_path}"
            )
            try:
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                data = {"status": stream_ready, "trigger": trigger}
                rpi_cloud_response = requests.post(post_url, data=(data), headers=headers)
                logger.info(f"RPI cloud server response: {rpi_cloud_response.text}")
            except (ConnectionError, InvalidURL):
                logger.error(
                    f"Error when posting wifi info to rpi cloud, check if rpi cloud server is running"
                )


cloud_notifier_service: CloudNotifier = CloudNotifier()
""" CloudNotifier service singleton"""
