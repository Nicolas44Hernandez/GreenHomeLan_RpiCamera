import logging
import time
from flask import Flask
from server.interfaces.gpio_interface import GpioButtonInterface
from server.managers.wifi_connection_manager import wifi_connection_manager_service
from server.notification import notification_service

logger = logging.getLogger(__name__)


class DoorBellManager:
    """Manager for Dorbell peripheral"""

    gpio_interface: GpioButtonInterface
    wifi_on_time_in_secs: int
    max_wifi_on_waitting_time_in_secs: int

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize DoorBellManager"""
        if app is not None:
            logger.info("initializing the DoorBellManager")

            self.wifi_on_time_in_secs = app.config["WIFI_ON_TIME_IN_SECS"]
            self.max_wifi_on_waitting_time_in_secs = app.config["MAX_WIFI_ON_WAITTING_TIME_IN_SECS"]
            self.gpio_interface = GpioButtonInterface(
                button_pin=app.config["PERIPHERALS_DOORBELL_BUTTON"],
                callback_function=self.doorbell_button_press_callback,
            )

    def doorbell_button_press_callback(self, channel):
        """Callback function for doorbell button press"""
        # Button debounce
        time.sleep(0.5)
        logger.info("Doorbell button pressed")

        # Notify the alarm to orchestrator
        notification_service.notify_alarm(alarm_type="doorbell", msg="doorbell pressed")

        # Request WiFi activation if needed
        wifi_connection_manager_service.wifi_temporary_activation(
            max_wifi_on_waitting_time_in_secs=self.max_wifi_on_waitting_time_in_secs,
            on_time_in_secs=self.wifi_on_time_in_secs,
        )


doorbell_manager_service: DoorBellManager = DoorBellManager()
""" Doorbell manager service singleton"""
