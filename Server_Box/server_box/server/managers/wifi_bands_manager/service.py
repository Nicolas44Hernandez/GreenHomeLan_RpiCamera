
import logging
from enum import Enum
from typing import Iterable
from flask import Flask
import yaml
from telnetlib import Telnet
from server.interfaces.wifi_interface import wifi_telnet_interface
from server.common import ServerBoxException, ErrorCode

# TODO: update commands
# TODO: update docupmentaiton
# TODO: refactor telnet commands call (group)

logger = logging.getLogger(__name__)

BANDS = ["2.4GHz","5GHz","6GHz"]

class Status(Enum):
    OFF = 0
    ON = 1

class WifiBandsManager: 
    """"""
    livebox_ip_address: str = None
    livebox_telnet_port: int = 23
    livebox_login: str = None
    livebox_password: str = None
    telnet_timeout_in_secs: float = 5
    telnet_commands = {}

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """ Initialize WifiBandsManager"""
        if app is not None:
            logger.debug("initializing the WifiBandsManager")
            # Initialize configuration
            self.livebox_ip_address = app.config["LIVEBOX_IP_ADDRESS"]
            self.livebox_telnet_port = app.config["LIVEBOX_TELNET_PORT"]
            self.livebox_login = app.config["LIVEBOX_LOGIN"]
            self.livebox_ip_password = app.config["LIVEBOX_PASSWORD"]
            self.telnet_timeout_in_secs = app.config["TELNET_TIMOUT_IN_SECS"]
            self.load_telnet_commands(app.config["LIVEBOX_TELNET_COMMANDS"])


    def create_telnet_connection(self) -> Telnet:
        # Create telnet connection
        return wifi_telnet_interface(
            host=self.livebox_ip_address, 
            port=self.livebox_telnet_port, 
            login=self.livebox_login, 
            password=self.livebox_ip_password,
            telnet_timeout_in_secs=self.telnet_timeout_in_secs,
        )                    

    def load_telnet_commands(self, commands_yaml_file: str):
        """Load the telnet commands dict from file"""
        logger.info("Telnet commands file: %s", commands_yaml_file)
        # Load logging configuration and configure flask application logger
        with open(commands_yaml_file) as stream:
            try:
                self.telnet_commands=yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise ServerBoxException(ErrorCode.TELNET_COMMANDS_FILE_ERROR)                
        
    def execute_telnet_commands(self, dictionary_keys: Iterable[str]):
        # Retreive commands
        new_element = self.telnet_commands
        for key in dictionary_keys:
            try:
                new_element = new_element[key]
            except: 
                logger.error("Item not found in tenlet commands: ", str[dictionary_keys])
                raise ServerBoxException(ErrorCode.TELNET_COMMAND_NOT_FOUND)
        
        commands = new_element        

        # If the command retrieved is not a str or a list command is wrong
        if not isinstance(commands, (str, list)):
            raise ServerBoxException(ErrorCode.TELNET_COMMAND_NOT_FOUND) 
        
        # create telnet connection
        telnet = self.create_telnet_connection()

        if isinstance(commands, str):
            # Execute telnet comand
            telnet.send_command(commands)

        elif isinstance(commands, list):
            # Loop over commands list
            for command in commands:
                # Execute telnet comand
                telnet.send_command(command)
        
        # Close telnet connection
        telnet.close()
    
    def get_module_version(self, module: str):
        """Execute module version in the livebox using telnet service"""        
        self.execute_telnet_commands(["SYSTEM",module + " version"])        

    def get_wifi_status(self):
        """Execute get wifi status command in the livebox using telnet service"""  
        self.execute_telnet_commands(["WIFI","status"])       

        #TODO: retreive livebox wifi status from return value 
        wifi_status = True
        return wifi_status

    def set_wifi_status(self, status: bool):
        """Execute set wifi status command in the livebox using telnet service"""  
        self.execute_telnet_commands(["WIFI",status]) 

        #TODO: retreive wifi livebox status from return value
        new_status = status
        return new_status
        
    def get_band_status(self, band: str):
        """Execute get wifi band status command in the livebox using telnet service"""  
        # Check if band number exists
        if band not in BANDS:
            raise ServerBoxException(ErrorCode.UNKNOWN_BAND_WIFI) 
        
        self.execute_telnet_commands(["WIFI", "bands", band, "status"]) 

        #TODO: retreive band status from livebox
        band_status = True
        return band_status

    def set_band_status(self, band: str, status):
        """Execute set wifi band status command in the livebox using telnet service"""  
        # Check if band number exists
        if band not in BANDS:
            raise ServerBoxException(ErrorCode.UNKNOWN_BAND_WIFI)

        self.execute_telnet_commands(["WIFI", "bands", band, status])        

        #TODO: retreive band status from livebox
        band_status = status
        return band_status


wifi_bands_manager_service: WifiBandsManager = WifiBandsManager()
""" Video manager Service singleton"""