"""
Thread dongle interface service
"""
import time
import logging
import threading
import serial
from server.common import ServerCameraException, ErrorCode
from queue import Queue, Empty


logger = logging.getLogger(__name__)


class ThreadClientDongle(threading.Thread):
    """Service class for thread client management"""

    thread_serial_port: str
    msg_callback: callable
    keep_alive_callback: callable
    serial_interface: serial.Serial

    def __init__(self, thread_serial_port: str):
        self.thread_serial_port = thread_serial_port
        self.msg_callback = None
        self.keep_alive_callback = None

        # Run Thread interface dedicated thread
        logger.info(f"Creatting serial interface object...")
        self.serial_interface = serial.Serial(
            self.thread_serial_port, 115200, stopbits=serial.STOPBITS_ONE
        )
        super(ThreadClientDongle, self).__init__(name="ThreadClientDongleThread")
        self.setDaemon(True)

    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b""):
            queue.put(line)
        out.close()

    def run_dedicated_thread(self):
        """Run Thread loop in dedicated if network is setted up"""
        logger.info(f"Running Thread loop in dedicated thread")
        try:
            self.start()
        except Exception as e:
            logger.error(e)

    def run(self):
        """Run thread"""

        while True:
            logger.info("loop....")
            if self.serial_interface.inWaiting() > 0:
                received_data = self.serial_interface.read(
                    self.serial_interface.inWaiting()
                )
                logger.info("Received data: ", received_data.decode("utf-8"))
            time.sleep(0.1)

    def set_msg_reception_callback(self, callback: callable):
        """Set Thread message reception callback"""
        self.msg_callback = callback

    def set_keep_alive_reception_callback(self, callback: callable):
        """Set Thread keep_alive reception callback"""
        self.keep_alive_callback = callback
