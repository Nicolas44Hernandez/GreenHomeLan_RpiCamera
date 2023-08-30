import logging
from datetime import timedelta
from timeloop import Timeloop
from flask import Flask
from server.interfaces.thread_interface import ThreadInterface

logger = logging.getLogger(__name__)

thread_keep_alive_timeloop = Timeloop()

class ThreadManager:
    """Manager for thread interface"""

    thread_interface: ThreadInterface
    serial_interface: str
    serial_speed: int
    thread_udp_port: int
    ipv6_mesh: str
    dataset_key: str
    device_id: str

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
            self.ipv6_mesh = app.config["THREAD_IPV6_MESH"]
            self.dataset_key = app.config["THREAD_DATSET_KEY"]
            self.device_id = app.config["THREAD_DEVICE_ID"]


            # Create Thread interface
            self.thread_interface = ThreadInterface(
                serial_interface=self.serial_interface,
                serial_speed=self.serial_speed,
                thread_udp_port=self.thread_udp_port,
            )

            logger.info(f"Join Thread network")

            if not self.thread_interface.setup_thread_node(
                ipv6_mesh=self.ipv6_mesh,
                dataset_key=self.dataset_key,
            ):
                logger.error(f"Error in thread node setup")
                return

            # Schedule keep alive messages
            self.schedule_thread_keep_alive_message_send()


    def send_keep_alive_message(self):
        """Send keep alive message via thread"""
        message = f"ka_{self.device_id}"
        logger.info("sending Thread keep alive msg")
        self.send_thread_message_to_border_router(message)

    def schedule_thread_keep_alive_message_send(self):
        """Schedule KA thread message"""

        @thread_keep_alive_timeloop.job(interval=timedelta(seconds=20))
        def send_keep_alive():
            self.send_keep_alive_message()

        thread_keep_alive_timeloop.start(block=False)


    def send_thread_message_to_border_router(self, message: str):
        """Send message to border router"""

        if self.thread_interface.running:
            self.thread_interface.send_message_to_border_router(message)
        else:
            logger.error(
                "Thread network not configured or not running, wating for network setup message"
            )
            logger.error("Message not published")

    def get_thread_network_setup(self):
        """Return thread network setup"""
        network_setup = {
            "ipv6_mesh": self.ipv6_mesh,
            "dataset_key": self.dataset_key,
        }
        return network_setup

thread_manager_service: ThreadManager = ThreadManager()
""" Thread manager service singleton"""
