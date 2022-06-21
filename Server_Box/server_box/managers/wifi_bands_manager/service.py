
import logging
from enum import Enum
from flask import Flask
import yaml
from telnetlib import Telnet
from server_box.interfaces.wifi_interface import wifi_telnet_interface

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
            self.load_telnet_commands(app.config["LIVEBOX_TELNET_COMMANDS"])


    def create_telnet_conneciton(self) -> Telnet:
        # Create telnet connection
        try: 
            return wifi_telnet_interface(
                host=self.livebox_ip_address, 
                port=self.livebox_telnet_port, 
                login=self.livebox_login, 
                password=self.livebox_ip_password
            )
        except: 
            # TODO: catch correct error type for not conected
            logger.error("telnet connection creation failed")            
            return None 

    def load_telnet_commands(self, commands_yaml_file: str):
        """Load the telnet commands dict from file"""
        logger.info("Telnet commands file: %s", commands_yaml_file)
        # Load logging configuration and configure flask application logger
        with open(commands_yaml_file) as stream:
            try:
                self.telnet_commands=yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.error("Error in telnet commands load, check commands file")
                logger.error(exc)
        
    def get_module_version(self, module: str):
        """Execute module version in the livebox using telnet service"""        
        telnet = self.create_telnet_conneciton()
        if telnet is None: 
            return None
        # Retrieve command for get module version
        try:
            command = self.telnet_commands["SYSTEM"][module + " version"]
        except: 
            logger.error("Module not found: ", module)
            return None
        # Execute telnet comand
        telnet.send_command(command)
        # Close telnet connection
        telnet.close()

    def get_wifi_status(self):
        """Execute get wifi status command in the livebox using telnet service"""  
        telnet = self.create_telnet_conneciton()
        if telnet is None:             
            return None
        # Retrieve command for get wifi status
        try:
            command = self.telnet_commands["WIFI"]["status"]
        except: 
            logger.error("Item not found in tenlet commands: WIFI[status]")
            return None
        # Execute telnet comand
        telnet.send_command(command)
        # Close telnet connection
        telnet.close()

        #TODO: retreive wifi status from livebox
        wifi_status = "WIFI: ON/OFF"
        return wifi_status

    def set_wifi_status(self, status: bool):
        """Execute set wifi status command in the livebox using telnet service"""  
        
        telnet = self.create_telnet_conneciton()
        if telnet is None:             
            return None
        # Retrieve command for get wifi status
        try:
            command = self.telnet_commands["WIFI"][status]
        except: 
            logger.error(
                f'Item not found in tenlet commands: WIFI[%s]',
                "ON" if status else "OFF"
            )
            return None
        # Execute telnet comand
        telnet.send_command(command)
        # Close telnet connection
        telnet.close()

        #TODO: retreive wifi status from livebox
        new_status = status
        return new_status
        
    def get_band_status(self, band: str):
        """Execute get wifi band status command in the livebox using telnet service"""  
        # Check if band number exists
        if band not in BANDS:
            # TODO: raise exception
            return None            
        telnet = self.create_telnet_conneciton()
        if telnet is None:
            # TODO: raise exception             
            return None
        # Retrieve command for get band status
        try:
            command = self.telnet_commands["WIFI"]["bands"][band]["status"]
        except: 
            logger.error("Item not found in tenlet commands: WIFI[bands][%s][status]", band)
            return None
        # Execute telnet comand
        telnet.send_command(command)
        # Close telnet connection
        telnet.close()

        #TODO: retreive band status from livebox
        band_status = True
        return band_status

    def set_band_status(self, band: str, status):
        """Execute set wifi band status command in the livebox using telnet service"""  
        # Check if band number exists
        if band not in BANDS:
            # TODO: raise exception
            return None            
        telnet = self.create_telnet_conneciton()
        if telnet is None:
            # TODO: raise exception             
            return None
        # Retrieve command for get band status
        try:
            command = self.telnet_commands["WIFI"]["bands"][band][status]
        except:             
            logger.error(
                "Item not found in tenlet commands: WIFI[bands][%s][%s]",
                band,
                "ON" if status else "OFF"
            )
            return None
        # Execute telnet comand
        telnet.send_command(command)
        # Close telnet connection
        telnet.close()

        #TODO: retreive band status from livebox
        band_status = status
        return band_status


wifi_bands_manager_service: WifiBandsManager = WifiBandsManager()
""" Video manager Service singleton"""