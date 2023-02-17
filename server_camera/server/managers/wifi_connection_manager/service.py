"""
Wifi connection manager service
"""
import logging
import socket
import threading
import time
import yaml
from datetime import datetime, timedelta
from timeloop import Timeloop
from datetime import timedelta
from flask import Flask
from server.managers.thread_manager import thread_manager_service
from server.common import ServerCameraException, ErrorCode

logger = logging.getLogger(__name__)

wifi_connection_status_timeloop = Timeloop()


class WifiConnectionManager:
    """Service class for Wifi connection status"""

    connected: bool
    polling_period_in_secs: int
    test_connection_address: str
    wifi_thread_commands = {}

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize WifiConnectionManager"""
        if app is not None:
            logger.info("initializing the WifiConnectionManager")

            self.polling_period_in_secs = app.config["WIFI_CONNECTION_STATUS_POLL_PERIOD_IN_SECS"]
            self.test_connection_address = app.config["TEST_CONNETION_IP"]
            self.load_wifi_thread_commands(app.config["WIFI_THREAD_COMMANDS"])

            # Schedule wifi connection status polling
            self.schedule_wifi_connection_status_polling()

    def load_wifi_thread_commands(self, commands_yaml_file: str):
        """Load the wifi thread commands dict from file"""
        logger.info("Wifi thread commands file: %s", commands_yaml_file)

        with open(commands_yaml_file) as stream:
            try:
                self.wifi_thread_commands = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise ServerCameraException(ErrorCode.WIFI_THREAD_COMMANDS_FILE_ERROR)

    def schedule_wifi_connection_status_polling(self):
        """Schedule the wifi connection status polling"""

        # Start wifi status polling service
        @wifi_connection_status_timeloop.job(
            interval=timedelta(seconds=self.polling_period_in_secs)
        )
        def poll_wifi_connection_status():
            # retrieve wifi connection status
            try:
                _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                _socket.connect((self.test_connection_address, 80))
                self.connected = True
            except OSError:
                self.connected = False
            _socket.close()

        wifi_connection_status_timeloop.start(block=False)

    def wifi_temporary_activation(
        self, max_wifi_on_waitting_time_in_secs: int, on_time_in_secs: int
    ):
        """Wait for WiFi temporary activation"""

        # If Wifi if not active, wait for activation
        # if self.connected:
        if False:
            logger.info("Already connected to Wifi")
        else:
            logger.info(f"Not connected to WiFi, waiting for connection")
            self.wait_for_connection_and_set_wifi_off_timer(
                max_wifi_on_waitting_time_in_secs=max_wifi_on_waitting_time_in_secs,
                wifi_on_time_in_secs=on_time_in_secs,
            )

    def turn_off_wifi(self):
        """send thread command to turn off wifi"""
        logger.info("Sendin WiFi OFF message via Thread")
        command = self.wifi_thread_commands["WIFI"]["BANDS"]["5GHz"][False]
        thread_manager_service.send_thread_message_to_border_router(command)

    def wait_for_connection_and_set_wifi_off_timer(
        self, max_wifi_on_waitting_time_in_secs: int, wifi_on_time_in_secs: int
    ):
        """Set Timer to turn off wifi"""
        now = datetime.now()
        wait_max_until = now + timedelta(seconds=max_wifi_on_waitting_time_in_secs)
        while not wifi_connection_manager_service.connected:
            if now > wait_max_until:
                logger.error("Wifi off watting timer expired, connection impossible")
                return
            time.sleep(1)
            now = datetime.now()
        logger.info(f"Connected to WiFi")
        logger.info(f"WiFi off command will be sent in {wifi_on_time_in_secs} secs")
        wifi_off_timer = threading.Timer(wifi_on_time_in_secs, self.turn_off_wifi)
        wifi_off_timer.start()


wifi_connection_manager_service: WifiConnectionManager = WifiConnectionManager()
""" WifiConnection manager service singleton"""
