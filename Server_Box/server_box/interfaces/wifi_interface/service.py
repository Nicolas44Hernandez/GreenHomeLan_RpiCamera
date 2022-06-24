import logging
import socket
import telnetlib
from server_box.common import ServerBoxException, ErrorCode

logger = logging.getLogger(__name__)

class Telnet:
    """Service class for telnet connection and commands management"""

    def __init__(
        self, 
        host: str,
        port: int = 23,
        login: str= None,
        password: str = None,
        telnet_timeout_in_secs: float=5
    ):
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.telnet_timeout_in_secs = telnet_timeout_in_secs
        self.connection = self.create_telnet_connection()
        
    def create_telnet_connection(self):
        # try to connect
        try: 
            tn_connection = telnetlib.Telnet(self.host, self.port, timeout=self.telnet_timeout_in_secs)
            tn_connection.read_until(b"login: ", timeout=self.telnet_timeout_in_secs)
            login = self.login + "\n"
            # Enter login
            tn_connection.write(login.encode("utf-8"))

            if self.password:
                tn_connection.read_until(b"Password: ", timeout=self.telnet_timeout_in_secs)
                password = self.password + "\n"
                # Enter password
                tn_connection.write(password.encode("utf-8"))            
        except (socket.timeout, socket.error):
            logger.error("Telnet connection creation failed")            
            raise ServerBoxException(ErrorCode.TELNET_CONNECTION_ERROR)

        logger.debug(f'Telnet connection established with host: %s', self.host)
        return tn_connection    
    
    def create_super_user_session(self):
        try:
            self.connection.write('sudo su\n'.encode('utf-8'))
            flag = self.login +":"
            self.connection.read_until(flag.encode('utf-8'), timeout=self.telnet_timeout_in_secs)
            password = self.password + "\n"
            # Enter password
            self.connection.write(password.encode("utf-8"))
        except (socket.timeout, socket.error):
            raise ServerBoxException(ErrorCode.TELNET_CONNECTION_ERROR)
        logger.debug('Super user session created')


    def close(self):
        try:
            self.connection.write(b"exit\n")
        except (socket.timeout, socket.error):
            raise ServerBoxException(ErrorCode.TELNET_CONNECTION_ERROR)
        logger.debug(f'Telnet connection closed with host: %s', self.host)
        

    def send_command(self, command: str):
        if 'sudo ' in command:
            self.create_super_user_session()
            filter = (self.login+"#").encode("utf-8")
        else: 
            filter = (self.login+"@").encode("utf-8")
        
        try:
            self.connection.read_until(filter, timeout=self.telnet_timeout_in_secs)
            command = command + "\n"
            self.connection.write(command.encode("utf-8"))
            self.log_command_output(command)
        except (socket.timeout, socket.error):
            raise ServerBoxException(ErrorCode.TELNET_CONNECTION_ERROR)


    def log_command_output(self, command: str):
        # TODO: process command result
        logger.debug("--------------------Executed command------------------------")
        logger.debug(f'Command:\n%s',command)        
        output = ""
        if 'sudo ' in command:
            filter = (self.login+"#").encode("utf-8")
        else: 
            filter = (self.login+"@").encode("utf-8")
        while True:                           
            try:
                data = self.connection.read_some() # read available data
            except (socket.timeout, socket.error):
                raise ServerBoxException(ErrorCode.TELNET_CONNECTION_ERROR)

            if any(x in data for x in [b"\n", b"~$"]):
                output += data.decode("utf-8")
            # check if it is the last line
            if filter in data:
                # remove last line
                output = output[:output.rfind('\n')]
                logger.debug(f'Output:\n%s',output)
                logger.debug("-------------------------------------------------------------")
                break

