import logging
import threading
import time
from datetime import datetime, timedelta
from flask import Flask
from server.interfaces.gpio_interface import GpioButtonInterface
from server.managers.wifi_connection_manager import wifi_connection_manager_service
from server.managers.thread_manager import thread_manager_service
from server.notification.cloud_notifier import cloud_notifier_service


logger = logging.getLogger(__name__)


class DoorBellManager:
    """Manager for Dorbell peripheral"""

    gpio_interface: GpioButtonInterface
    status: bool
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
        time.sleep(0.2)
        logger.info("Doorbell button pressed")

        # If Wifi if not active, send thread command to activate it
        if not wifi_connection_manager_service.connected:
            wifi_on_command = self.wifi_thread_commands["WIFI"]["BANDS"]["5GHz"][True]
            logger.info(f"Not connected to Wifi, sending command: {wifi_on_command}")
            thread_manager_service.send_thread_message_to_border_router(wifi_on_command)
            self.set_wifi_off_timer()
        else:
            logger.info("Already connected to Wifi")

        # Notify cloud server to video stream is ready
        cloud_notifier_service.notify_video_stream_ready(stream_ready=True)

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
                logger.error("Wifi on watting timer")
                return
            time.sleep(1)
            now = datetime.now()
        logger.info(f"wifi off command will be sent in {self.wifi_on_time_in_secs} secs")
        wifi_off_timer = threading.Timer(self.wifi_on_time_in_secs, self.turn_off_wifi)
        wifi_off_timer.start()


doorbell_manager_service: DoorBellManager = DoorBellManager()
""" Doorbell manager service singleton"""
