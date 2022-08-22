import logging
from typing import Iterable
from flask import Flask
import requests

from server.managers.wifi_bands_manager import wifi_bands_manager_service
from server.interfaces.thread_interface import ThreadInterface, ThreadNode
from server.common import ServerBoxException, ErrorCode

logger = logging.getLogger(__name__)


class ThreadManager:
    """Manager for thread interface"""

    thread_interface: ThreadInterface

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize ThreadManager"""
        if app is not None:
            logger.debug("initializing the ThreadManager")

            # TODO: Veryfy that WIFI is ON before continue otherwise turn it on

            # setup thread interface
            self.thread_interface = ThreadInterface(
                sudo_password=app.config["SUDO_PASSWORD"],
                thread_network_config_file=app.config["THREAD_NETWORK_CONFIG"],
            )

    def send_thread_network_info_to_node(self, node_name: str):
        """send thread network config to node"""

        dest_node: ThreadNode = None
        for node in self.thread_interface.getNodes():
            if node.name == node_name:
                dest_node = node
                break

        # Sanity check
        if dest_node is None:
            raise ServerBoxException(ErrorCode.THREAD_NODE_NOT_CONFIGURED)

        # send network info to node server
        # TODO: try catch
        node_response = requests.post(dest_node.url, json=self.thread_network_setup)
        logger.debug(f"Node server response: {node_response.text}")

    def send_thread_network_info_to_all_nodes(self):
        """send thread network config to all the nodes"""
        for node in self.thread_interface.getNodes():
            self.send_thread_network_info_to_node(node.name)

    def get_thread_nodes(self) -> Iterable[ThreadNode]:
        """return all the configured thread nodes"""
        nodes = self.thread_interface.getNodes()
        return nodes

    def get_node_mac(self, node_name: str):
        """return the mac node address"""
        node_to_find: ThreadNode = None
        for node in self.thread_interface.getNodes():
            if node.name == node_name:
                node_to_find = node
                break

        # Sanity check
        if node_to_find is None:
            raise ServerBoxException(ErrorCode.THREAD_NODE_NOT_CONFIGURED)

        return node_to_find.mac


thread_manager_service: ThreadManager = ThreadManager()
""" Thread manager service singleton"""
