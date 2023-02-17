import logging
import time
from flask import Flask
from server.managers.wifi_connection_manager import wifi_connection_manager_service
from server.notification import notification_service
from server.interfaces.gpio_interface.service import GpioMotionSensorInterface

logger = logging.getLogger(__name__)


class PresenceDetectionManager:
    """Manager for presence detection peripheral"""

    gpio_interface: GpioMotionSensorInterface
    wifi_on_time_in_secs: int
    max_wifi_on_waitting_time_in_secs: int

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize PresenceDetectionManager"""
        if app is not None:
            logger.info("initializing the PresenceDetectionManager")

            self.wifi_on_time_in_secs = app.config["WIFI_ON_TIME_IN_SECS"]
            self.max_wifi_on_waitting_time_in_secs = app.config["MAX_WIFI_ON_WAITTING_TIME_IN_SECS"]
            self.gpio_interface = GpioMotionSensorInterface(
                sensor_pin=app.config["PERIPHERALS_PRESENCE_DETECTION_PIN"],
                callback_function=self.presence_detection_callback,
            )

    def presence_detection_callback(self, channel):
        """Callback function for presence detection"""
        # Sensor debounce
        time.sleep(0.2)
        logger.info("Presence detected")

        # Notify the alarm to orchestrator
        notification_service.notify_alarm(alarm_type="presence", msg="presence detected")

        # Request WiFi activation if needed
        wifi_connection_manager_service.wifi_temporary_activation(
            max_wifi_on_waitting_time_in_secs=self.max_wifi_on_waitting_time_in_secs,
            on_time_in_secs=self.wifi_on_time_in_secs,
        )


presence_detection_manager_service: PresenceDetectionManager = PresenceDetectionManager()
""" Presence detection manager service singleton"""
