import logging
from timeloop import Timeloop
from datetime import timedelta
from flask import Flask
from server.interfaces.thread_dongle_interface import ThreadDongleInterface

logger = logging.getLogger(__name__)

thread_keep_alive_timeloop = Timeloop()


class ThreadManager:
    """Manager for thread interface"""

    thread_dongle_interface: ThreadDongleInterface
    serial_interface: str
    serial_speed: int
    keep_alive_message_period_in_secs: int
    device_id: int

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
            self.keep_alive_message_period_in_secs = app.config[
                "THREAD_KEEP_ALIVE_MSG_PERIOD_IN_SECS"
            ]
            self.device_id = app.config["THREAD_DEVICE_ID"]

            # Create Thread interface
            self.thread_dongle_interface = ThreadDongleInterface(
                thread_serial_port=self.serial_interface,
                serial_speed=self.serial_speed,
            )

            # Run thread donfgle interface in dedicated thread
            self.thread_dongle_interface.run_dedicated_thread()

            # Schedule keep alive messages sending
            self.schedule_ka_message_sending()

    def schedule_ka_message_sending(self):
        """Schedule the keep alive message sending"""

        # Start wifi status polling service
        @thread_keep_alive_timeloop.job(
            interval=timedelta(seconds=self.keep_alive_message_period_in_secs)
        )
        def send_ka_message():
            # Send keep alive message via thread
            logger.info(f"Sending thread keep alive message")
            ka_msg = f"ka_{self.device_id}"
            self.send_thread_message_to_border_router(ka_msg)

        thread_keep_alive_timeloop.start(block=False)

    def send_thread_message_to_border_router(self, message: str):
        """Send message to border router"""

        msg = f"{message} "
        if not self.thread_dongle_interface.send_message_to_border_router(message=msg):
            logger.error(
                "Thread network not configured or not running, wating for network setup message"
            )
            logger.error("Message not published")


thread_manager_service: ThreadManager = ThreadManager()
""" Thread manager service singleton"""
