import logging
import yaml
from flask import Flask
from server.interfaces.gpio_interface import GpioInterface
from server.managers.wifi_connection_manager import wifi_connection_manager_service
from server.managers.thread_manager import thread_manager_service
from server.common import ServerCameraException, ErrorCode

logger = logging.getLogger(__name__)


class DoorBellManager:
    """Manager for Dorbell peripheral"""

    gpio_interface: GpioInterface
    status: bool
    wifi_thread_commands = {}

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize DoorBellManager"""
        if app is not None:
            logger.info("initializing the DoorBellManager")

            self.load_wifi_thread_commands(app.config["WIFI_THREAD_COMMANDS"])
            self.gpio_interface = GpioInterface(
                doorbell_button=app.config["PERIPHERALS_DOORBELL_BUTTON"],
                callback_function=self.doorbell_button_press_callback,
            )

    def load_wifi_thread_commands(self, commands_yaml_file: str):
        """Load the wifi thread commands dict from file"""
        logger.info("Wifi thread commands file: %s", commands_yaml_file)

        with open(commands_yaml_file) as stream:
            try:
                self.wifi_thread_commands = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise ServerCameraException(ErrorCode.WIFI_THREAD_COMMANDS_FILE_ERROR)

    def doorbell_button_press_callback(self, channel):
        """Callback function for doorbell button press"""
        logger.info("Doorbell button pressed")
        logger.info(self.wifi_thread_commands["WIFI"]["ALL"][True])
        # If Wifi if not active, send thread command to activate it
        if not wifi_connection_manager_service.connected:
            thread_manager_service.send_thread_message_to_border_router(
                self.wifi_thread_commands["WIFI"]["ALL"][True]
            )


doorbell_manager_service: DoorBellManager = DoorBellManager()
""" Doorbell manager service singleton"""
