import logging
from flask import Flask

from server.interfaces.thread_interface import ThreadInterface
from server.common import ServerCameraException, ErrorCode

logger = logging.getLogger(__name__)


class ThreadManager:
    """Manager for thread interface"""

    thread_interface: ThreadInterface
    serial_interface: str
    serial_speed: int
    thread_udp_port: int

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


thread_manager_service: ThreadManager = ThreadManager()
""" Thread manager service singleton"""
