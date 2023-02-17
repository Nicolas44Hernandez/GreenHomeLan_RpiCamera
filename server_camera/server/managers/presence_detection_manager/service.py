import logging
import threading
import time
import yaml
from datetime import datetime, timedelta
from flask import Flask
from server.managers.wifi_connection_manager import wifi_connection_manager_service
from server.managers.thread_manager import thread_manager_service
from server.notification import notification_service
from server.interfaces.gpio_interface.service import GpioMotionSensorInterface
from server.common import ServerCameraException, ErrorCode


logger = logging.getLogger(__name__)


class PresenceDetectionManager:
    """Manager for presence detection peripheral"""

    gpio_interface: GpioMotionSensorInterface
    wifi_thread_commands = {}
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
            self.load_wifi_thread_commands(app.config["WIFI_THREAD_COMMANDS"])
            self.gpio_interface = GpioMotionSensorInterface(
                sensor_pin=app.config["PERIPHERALS_PRESENCE_DETECTION_PIN"],
                callback_function=self.presence_detection_callback,
            )

    def load_wifi_thread_commands(self, commands_yaml_file: str):
        """Load the wifi thread commands dict from file"""
        logger.info("Wifi thread commands file: %s", commands_yaml_file)

        with open(commands_yaml_file) as stream:
            try:
                self.wifi_thread_commands = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise ServerCameraException(ErrorCode.WIFI_THREAD_COMMANDS_FILE_ERROR)

    # TODO: mutualize wifi on / off commands
    def presence_detection_callback(self, channel):
        """Callback function for presence detection"""
        # Sensor debounce
        time.sleep(0.2)
        logger.info("Presence detected")

        # Notify the alarm to orchestrator
        notification_service.notify_alarm(alarm_type="presence", msg="presence detected")

        # If Wifi if not active, wait for activation
        if not wifi_connection_manager_service.connected:
            logger.info(f"Not connected to WiFi, waiting for connection")
            self.set_wifi_off_timer()
        else:
            logger.info("Already connected to Wifi")

    def turn_off_wifi(self):
        """send thread command to turn off wifi"""
        thread_manager_service.send_thread_message_to_border_router(
            self.wifi_thread_commands["WIFI"]["BANDS"]["5GHz"][False]
        )

    def set_wifi_off_timer(self):
        """Set Timer to turn off wifi"""
        now = datetime.now()
        wait_max_until = now + timedelta(seconds=self.max_wifi_on_waitting_time_in_secs)
        while not wifi_connection_manager_service.connected:
            if now > wait_max_until:
                logger.error("Wifi off watting timer expired, connection impossible")
                return
            time.sleep(1)
            now = datetime.now()
        logger.info(f"WiFi off command will be sent in {self.wifi_on_time_in_secs} secs")
        wifi_off_timer = threading.Timer(self.wifi_on_time_in_secs, self.turn_off_wifi)
        wifi_off_timer.start()


presence_detection_manager_service: PresenceDetectionManager = PresenceDetectionManager()
""" Presence detection manager service singleton"""
