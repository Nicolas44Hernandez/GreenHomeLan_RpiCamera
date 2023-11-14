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
    serial_interface: serial.Serial

    def __init__(self, thread_serial_port: str):
        self.thread_serial_port = thread_serial_port

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
            if self.serial_interface.inWaiting() > 0:
                received_data = self.serial_interface.read(
                    self.serial_interface.inWaiting()
                )
                logger.info(f"Received data:%s ", received_data.decode("utf-8"))
                self.send_message_to_border_router("MSG")
                # TODO: Specify received messages and what to do (callbacks)
            time.sleep(0.1)

    def send_message_to_border_router(self, message: str):
        """Send thread message to Border router"""

        message = "~" + message + "#"
        logger.info("Sending msg: ", message)
        ret = self.serial_interface.write(message.encode("utf-8"))
        # TODO: manage return values and exceptions

        if ret != 0:
            return True
        return False
