"""
Thread interface service
"""
import logging
import time
from server.common import ServerCameraException, ErrorCode
import serial

logger = logging.getLogger(__name__)

SERIAL_READ_TIMEOUT_IN_SECS = 0.1


class ThreadNode:
    """Service class for thread node"""

    ipv6_otbr: str
    ipv6_mesh: str
    dataset_key: str
    serial: serial.Serial
    thread_udp_port: int
    running: bool

    def __init__(
        self,
        serial_interface: str,
        serial_speed: int,
        thread_udp_port: int,
    ):

        logger.info(f"serial_interface: {serial_interface}")
        logger.info(f"serial_speed: {serial_speed}")
        logger.info(f"thread_udp_port: {thread_udp_port}")

        self.serial = serial.Serial(serial_interface, serial_speed)

        self.thread_udp_port = thread_udp_port
        self.running = False
        self.dataset_key = {}

    def setup_thread_node(self, ipv6_otbr: str, ipv6_mesh: str, dataset_key: str) -> bool:
        """Thread node configuration and setup"""

        logger.info("Thread node setup")
        logger.info(f"host_ipv6_addr: {ipv6_otbr}")
        logger.info(f"host_ipv6_mesh: {ipv6_mesh}")
        logger.info(f"dataset_key: {dataset_key}")

        self.ipv6_otbr = ipv6_otbr
        self.ipv6_mesh = ipv6_mesh
        self.dataset_key = dataset_key

        try:
            # join Thread network
            logger.info("Join thread network")
            self.send_serial_command(f"ifconfig down")
            self.send_serial_command(f"udp close")
            self.send_serial_command(f"dataset set active {self.dataset_key}")
            self.send_serial_command(f"ifconfig up")
            self.send_serial_command(f"thread start")

            # Check that node has joined the Thread network
            logger.info("Verify connection")
            self.send_serial_command(f"state")
            self.send_serial_command(f"netdata show")
            self.send_serial_command(f"ipaddr")

            # Ping Thread border router
            logger.info("Ping thread border router")
            self.send_serial_command(f"ping {self.ipv6_otbr}")

            # Open UDP connection
            logger.info("Ope udp port")
            self.send_serial_command(f"udp open")
            self.send_serial_command(f"udp connect {self.ipv6_mesh} {self.thread_udp_port}")

            self.running = True
            logger.info(f"Thread Node running")
            return True
        except:
            self.running = False
            logger.error(f"Error in thread network setup, Thread Node is not running")
            return False

    def send_serial_command(self, command: str):
        """Send Serial command"""
        try:
            command = command + "\n"
            self.serial.write(command.encode())
            quantity = self.serial.in_waiting
            response = ""
            time.sleep(2)
            while True:
                if quantity > 0:
                    response += str(self.serial.read(quantity))
                else:
                    time.sleep(SERIAL_READ_TIMEOUT_IN_SECS)
                quantity = self.serial.in_waiting
                if quantity == 0:
                    break

            logger.info(f"Command: {command.strip()}")
            logger.info(f"Response: {response}")
            return True, response
        except Exception as e:
            logger.info(f"Error sending command")
            return False, None

    def send_message_to_border_router(self, message: str):
        """Send thread message to Border router"""

        message = "udp send " + message
        sent, response = self.send_serial_command(message)
        if not sent:
            self.running = False
        return sent, response
