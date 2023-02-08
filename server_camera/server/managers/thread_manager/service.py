import logging
from flask import Flask
from server.managers.mqtt_manager import mqtt_manager_service
from server.interfaces.thread_interface import ThreadInterface

logger = logging.getLogger(__name__)


class ThreadManager:
    """Manager for thread interface"""

    thread_interface: ThreadInterface
    serial_interface: str
    serial_speed: int
    mqtt_thread_network_params_topic: str
    thread_network_config: dict
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
            self.thread_network_config = None
            self.serial_interface = app.config["THREAD_SERIAL_INTERFACE"]
            self.serial_speed = app.config["THREAD_SERIAL_SPEED"]
            self.thread_udp_port = app.config["THREAD_UDP_PORT"]
            self.mqtt_thread_network_params_topic = app.config["MQTT_THREAD_NETWORK_INFO_TOPIC"]

            # retrieve RPI box ip
            self.rpi_box_ip = app.config["RPI_BOX_IP"]
            self.rpi_box_port = app.config["RPI_BOX_PORT"]
            self.rpi_box_path = app.config["RPI_BOX_THREAD_PATH"]

            # Create Thread interface
            self.thread_interface = ThreadInterface(
                serial_interface=self.serial_interface,
                serial_speed=self.serial_speed,
                thread_udp_port=self.thread_udp_port,
            )

            # Subscribe to relays command MQTT topic
            mqtt_manager_service.subscribe_to_topic(
                topic=self.mqtt_thread_network_params_topic,
                callback=self.thread_network_params_callback,
            )

    def thread_network_params_callback(self, thread_network_config: dict):
        """Callback for MQTT receive thread network params """""

        if not self.thread_interface.running:
            logger.info(f"Join Thread network, interface setup")
            logger.info(
                f"Thread network params received: {thread_network_config}")

            if self.thread_interface.setup_thread_node(
                ipv6_otbr=thread_network_config["ipv6_otbr"],
                ipv6_mesh=thread_network_config["ipv6_mesh"],
                dataset_key=thread_network_config["dataset_key"]
            ):
                self.thread_network_config = thread_network_config
            else:
                self.thread_network_config = None
                logger.error(f"Error in thread node setup")

        self.send_thread_message_to_border_router("holis")

    def send_thread_message_to_border_router(self, message: str):
        """Send message to border router"""

        if self.thread_interface.running:
            self.thread_interface.send_message_to_border_router(message)
        else:
            logger.error(
                "Thread network not configured or not running, wating for network setup message")
            logger.error("Message not published")

    def get_thread_network_setup(self):
        """Retrieve thread network config"""

        return self.thread_network_config


thread_manager_service: ThreadManager = ThreadManager()
""" Thread manager service singleton"""
