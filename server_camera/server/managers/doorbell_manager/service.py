import logging
from flask import Flask

from server.interfaces.thread_interface import ThreadInterface
from server.interfaces.gpio_interface import GpioInterface

logger = logging.getLogger(__name__)


class DoorBellManager:
    """Manager for Dorbell peripheral"""

    gpio_interface: GpioInterface
    status: bool

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize DoorBellManager"""
        if app is not None:
            logger.info("initializing the DoorBellManager")

            self.gpio_interface = GpioInterface(
                doorbell_button=app.config["PERIPHERALS_DOORBELL_BUTTON"],
                callback_function=self.doorbell_button_press_callback,
            )

    def doorbell_button_press_callback(self, channel):
        """Callback function for doorbell button press"""
        logger.info("Doorbell button pressed")


doorbell_manager_service: DoorBellManager = DoorBellManager()
""" Doorbell manager service singleton"""
