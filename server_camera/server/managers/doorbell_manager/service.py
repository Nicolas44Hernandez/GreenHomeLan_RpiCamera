import logging
import requests
import yaml
import threading
import time
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError, InvalidURL
from flask import Flask
from server.interfaces.gpio_interface import GpioInterface
from server.managers.wifi_connection_manager import wifi_connection_manager_service
from server.managers.thread_manager import thread_manager_service
from server.managers.ip_discovery import IpDiscoveryService as ip_discovery_service
from server.common import ServerCameraException, ErrorCode


logger = logging.getLogger(__name__)


class DoorBellManager:
    """Manager for Dorbell peripheral"""

    gpio_interface: GpioInterface
    status: bool
    wifi_thread_commands = {}
    wifi_on_time_in_secs: int
    max_wifi_on_waitting_time_in_secs: int
    rpi_cloud_ip: str = None
    rpi_cloud_port: str
    rpi_cloud_video_stream_path: str

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize DoorBellManager"""
        if app is not None:
            logger.info("initializing the DoorBellManager")

            self.wifi_on_time_in_secs = app.config["WIFI_ON_TIME_IN_SECS"]
            self.max_wifi_on_waitting_time_in_secs = app.config["MAX_WIFI_ON_WAITTING_TIME_IN_SECS"]
            self.load_wifi_thread_commands(app.config["WIFI_THREAD_COMMANDS"])
            self.gpio_interface = GpioInterface(
                doorbell_button_pin=app.config["PERIPHERALS_DOORBELL_BUTTON"],
                callback_function=self.doorbell_button_press_callback,
            )

            # retrieve RPI box ip
            self.rpi_cloud_ip = ip_discovery_service.get_ip_addr(mac=app.config["RPI_CLOUD_MAC"])
            self.rpi_cloud_port = app.config["RPI_CLOUD_PORT"]
            self.rpi_cloud_video_stream_path = app.config["RPI_CLOUD_DOORBELL_PATH"]

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
        self.notify_video_stream_ready_to_rpi_cloud(stream_ready=True)

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

    def notify_video_stream_ready_to_rpi_cloud(self, stream_ready: bool):
        """Call HTTP post to notify video stream status to rpi cloud"""

        logger.info(f"Posting HTTP to notify video stream status {stream_ready} to RPI cloud")

        # Post video stream status to rpi cloud
        post_url = (
            f"http://{self.rpi_cloud_ip}:{self.rpi_cloud_port}/{self.rpi_cloud_video_stream_path}"
        )
        try:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {"status": stream_ready}
            rpi_cloud_response = requests.post(post_url, data=(data), headers=headers)
            logger.info(f"RPI cloud server response: {rpi_cloud_response.text}")
        except (ConnectionError, InvalidURL):
            logger.error(
                f"Error when posting wifi info to rpi cloud, check if rpi cloud server is running"
            )


doorbell_manager_service: DoorBellManager = DoorBellManager()
""" Doorbell manager service singleton"""
