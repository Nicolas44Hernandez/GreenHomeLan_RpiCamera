import logging
from timeloop import Timeloop
from flask import Flask
from server.interfaces.thread_dongle_interface import ThreadDongleInterface

logger = logging.getLogger(__name__)

thread_keep_alive_timeloop = Timeloop()


class ThreadManager:
    """Manager for thread interface"""

    thread_dongle_interface: ThreadDongleInterface
    serial_interface: str
    serial_speed: int

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize ThreadManager"""
        if app is not None:
            logger.info("initializing the ThreadManager")
            self.thread_dongle_interface = None
            self.serial_interface = app.config["THREAD_SERIAL_INTERFACE"]
            self.serial_speed = app.config["THREAD_SERIAL_SPEED"]

            # Create Thread interface
            self.thread_dongle_interface = ThreadDongleInterface(
                thread_serial_port=self.serial_interface
            )

            # Run thread donfgle interface in dedicated thread
            self.thread_dongle_interface.run_dedicated_thread()

    def send_thread_message_to_border_router(self, message: str):
        """Send message to border router"""

        if not self.thread_dongle_interface.send_message_to_border_router(
            message=message
        ):
            logger.error(
                "Thread network not configured or not running, wating for network setup message"
            )
            logger.error("Message not published")


thread_manager_service: ThreadManager = ThreadManager()
""" Thread manager service singleton"""
