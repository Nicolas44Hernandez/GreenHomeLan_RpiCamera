import logging
import json
from flask import Flask
import requests
from requests.exceptions import ConnectionError, InvalidURL
from server.interfaces.thread_interface import ThreadInterface
from server.managers.ip_discovery import IpDiscoveryService as ip_discovery_service
from server.common import ServerCameraException, ErrorCode

logger = logging.getLogger(__name__)


class ThreadManager:
    """Manager for thread interface"""

    thread_interface: ThreadInterface
    serial_interface: str
    serial_speed: int
    thread_udp_port: int
    rpi_box_ip: str = None
    threadrpi_box_port: str
    threadrpi_box_path: str

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize ThreadManager"""
        if app is not None:
            logger.info("initializing the ThreadManager")

            self.thread_interface = None
            self.serial_interface = app.config["THREAD_SERIAL_INTERFACE"]
            self.serial_speed = app.config["THREAD_SERIAL_SPEED"]
            self.thread_udp_port = app.config["THREAD_UDP_PORT"]

            # retrieve RPI box ip
            self.rpi_box_ip = ip_discovery_service.get_ip_addr(mac=app.config["RPI_BOX_MAC"])
            self.rpi_box_port = app.config["RPI_BOX_PORT"]
            self.rpi_box_path = app.config["RPI_BOX_PATH"]

            thread_network_config = self.retrieve_thread_network_config()

            self.join_thread_network(
                ipv6_otbr=thread_network_config["ipv6_otbr"],
                ipv6_mesh=thread_network_config["ipv6_mesh"],
                dataset_key=thread_network_config["dataset_key"],
            )

    def retrieve_thread_network_config(self):
        """Get thread network config from rpi box"""
        # Sanity check
        if self.rpi_box_ip is None:
            raise ServerCameraException(ErrorCode.THREAD_NODE_NOT_CONFIGURED)

        # retrieve thread network config from border router
        url = f"http://{self.rpi_box_ip}:{self.rpi_box_port}/{self.rpi_box_path}"
        try:
            response = requests.get(url)
            thread_network_setup = json.loads(response.text)
            logger.info(f"Server response: {thread_network_setup}")
            return thread_network_setup
        except (ConnectionError, InvalidURL):
            logger.error(
                f"Error when getting network info from rpi box, check if server is running"
            )
            return False

    def join_thread_network(
        self,
        ipv6_otbr: str,
        ipv6_mesh: str,
        dataset_key: str,
    ):
        """Join Thread network, interface setup"""

        self.thread_interface = ThreadInterface(
            ipv6_otbr=ipv6_otbr,
            ipv6_mesh=ipv6_mesh,
            dataset_key=dataset_key,
            serial_interface=self.serial_interface,
            serial_speed=self.serial_speed,
            thread_udp_port=self.thread_udp_port,
        )

    def send_thread_message_to_border_router(self, message: str):
        """Send message to border router"""

        if self.thread_interface is None:
            raise ServerCameraException(ErrorCode.THREAD_NODE_NOT_CONFIGURED)

        self.thread_interface.send_message_to_border_router(message)

    def get_thread_network_setup(self):
        """Retrieve thread network config"""

        return self.thread_interface


thread_manager_service: ThreadManager = ThreadManager()
""" Thread manager service singleton"""
