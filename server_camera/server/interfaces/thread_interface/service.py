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

    host_ipv6_addr: str
    host_ipv6_mesh: str
    dataset_key: str
    serial: serial.Serial
    thread_udp_port: int

    def __init__(
        self,
        host_ipv6_addr: str,
        host_ipv6_mesh: str,
        dataset_key: str,
        serial_interface: str,
        serial_speed: int,
        thread_udp_port: int,
    ):

        logger.info(f"Creating Thread interface:")
        logger.info(f"host_ipv6_addr: {host_ipv6_addr}")
        logger.info(f"host_ipv6_mesh: {host_ipv6_mesh}")
        logger.info(f"dataset_key: {dataset_key}")
        logger.info(f"serial_interface: {serial_interface}")
        logger.info(f"serial_speed: {serial_speed}")
        logger.info(f"thread_udp_port: {thread_udp_port}")

        self.host_ipv6_addr = host_ipv6_addr
        self.host_ipv6_mesh = host_ipv6_mesh
        self.dataset_key = dataset_key
        self.serial = serial.Serial(serial_interface, serial_speed)
        self.thread_udp_port = thread_udp_port

        # setup thread node
        self.setup_thread_node()

    def setup_thread_node(self):
        """Thread node configuration and setup"""
        # join Thread network
        logger("Join thread network")
        self.send_serial_command(f"dataset set active {self.dataset_key}")
        self.send_serial_command(f"ifconfig up")
        self.send_serial_command(f"thread start")

        # Check that node has joined the Thread network
        logger("Verify connection")
        self.send_serial_command(f"state")
        self.send_serial_command(f"netdata show")
        self.send_serial_command(f"ipaddr")

        # Ping Thread border router
        logger("Ping thread border router")
        self.send_serial_command(f"ping {self.host_ipv6_addr}")

        # Open UDP connection
        logger("Ope udp port")
        self.send_serial_command(f"udp open")
        self.send_serial_command(f"udp connect {self.host_ipv6_mesh} {self.thread_udp_port}")

    def send_serial_command(self, command: str):
        """Send Serial command"""
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

        logger.info(f"Command: {command}")
        logger.info(f"Response: {response}")
