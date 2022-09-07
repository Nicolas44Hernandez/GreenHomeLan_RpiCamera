"""
Video capture interface service
"""
import logging
import subprocess
import shlex
import threading


logger = logging.getLogger(__name__)


class VideoManagerInterface(threading.Thread):
    """Service class for video manager interface management"""

    fps : int


    def __init__(self, sudo_password: str, thread_network_config_file: str):
        self.sudo_password = sudo_password
        self.msg_callback = None

        # Running flag
        self.running = True

        # Call Super constructor
        super(VideoManagerInterface, self).__init__(name="VideoManagerInterfaceThread")
        self.setDaemon(True)

    def run(self):
        """Run thread"""
        while self.running:
            # Capture
