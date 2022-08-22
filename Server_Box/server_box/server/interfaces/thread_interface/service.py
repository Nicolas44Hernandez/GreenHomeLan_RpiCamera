"""
Thread interface service
"""
import logging
import yaml
import subprocess
from typing import Iterable
from server.common import ServerBoxException, ErrorCode

logger = logging.getLogger(__name__)


class ThreadNode:
    """Thread nodes model"""

    name: str
    mac: str
    url: str

    def __init__(self, name: str, mac: str, url: str):
        self.name = name
        self.mac = mac
        self.url = url


class Thread:
    """Service class for thread network setup management"""

    sudo_password: str
    thread_network_setup = {}
    nodes = Iterable[ThreadNode]

    def __init__(self, sudo_password: str, thread_network_config_file: str):
        self.sudo_password = sudo_password
        # setup thread network
        self.setup_thread_network(thread_network_config_file)

    def setup_thread_network(self, thread_network_config_file: str):
        """Setup the thread network"""
        logger.info("Thread network config file: %s", thread_network_config_file)

        # Load Thread network configuration
        with open(thread_network_config_file) as stream:
            try:
                configuration = yaml.safe_load(stream)
                self.nodes = [
                    ThreadNode(name=node["name"], mac=node["mac"], url=node["server_url"])
                    for node in configuration["THREAD"]["NODES"]
                ]
            except (yaml.YAMLError, KeyError) as exc:
                raise ServerBoxException(ErrorCode.THREAD_CONFIG_FILE_ERROR)

        # Thread network initialisation (ot-cli)
        for command in configuration["THREAD"]["NETWORK_SETUP_COMMANDS"]:
            # run command
            cmd = command.split()
            # TODO: try exception
            cmd1 = subprocess.Popen(["echo", self.sudo_password], stdout=subprocess.PIPE)
            cmd2 = subprocess.Popen(["sudo", "-S"] + cmd, stdin=cmd1.stdout, stdout=subprocess.PIPE)
            if "ipaddr" in command:
                output = cmd2.stdout.read().decode()
                self.thread_network_setup["ip6v_otbr"] = output[-3]
                self.thread_network_setup["ip6v_mesh"] = output[-4]
            elif "dataset active -x" in command:
                output = cmd2.stdout.read().decode()
                self.thread_network_setup["dataset"] = output[-3]
        logger.debug(f"Thread network config: {self.thread_network_setup}")

    def getNodes(self) -> Iterable[ThreadNode]:
        """Returns the configured nodes"""
        return self.nodes
