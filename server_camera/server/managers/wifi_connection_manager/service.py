"""
Wifi connection manager service
"""
import logging
import socket
from timeloop import Timeloop
from datetime import timedelta
from flask import Flask

logger = logging.getLogger(__name__)

wifi_connection_status_timeloop = Timeloop()


class WifiConnectionManager:
    """Service class for Wifi connection status"""

    connected: bool
    polling_period_in_secs: int

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize WifiConnectionManager"""
        if app is not None:
            logger.info("initializing the WifiConnectionManager")

            self.polling_period_in_secs = app.config["WIFI_CONNECTION_STATUS_POLL_PERIOD_IN_SECS"]

            # Schedule wifi connection status polling
            self.schedule_wifi_connection_status_polling()

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
                _socket.connect(("192.168.1.45", 80))
                self.connected = True
            except OSError:
                self.connected = False
            _socket.close()
            logger.info(f"Wifi interface status: {self.connected}")

        wifi_connection_status_timeloop.start(block=False)


wifi_connection_manager_service: WifiConnectionManager = WifiConnectionManager()
""" WifiConnection manager service singleton"""
