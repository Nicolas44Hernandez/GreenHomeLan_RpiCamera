import logging
import telnetlib

logger = logging.getLogger(__name__)

#TODO: ADD Timer in read_until

class Telnet:
    """Service class for telnet connection and commands management"""

    def __init__(self, host: str, port: int = 23, login: str= None, password: str = None):
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.connection = self.create_telnet_connection()
        
    def create_telnet_connection(self):
        # try to connect
        tn_connection = telnetlib.Telnet(self.host, self.port)
        tn_connection.read_until(b"login: ")
        login = self.login + "\n"
        # Enter login
        tn_connection.write(login.encode("utf-8"))

        if self.password:
            tn_connection.read_until(b"Password: ")
            password = self.password + "\n"
            # Enter password
            tn_connection.write(password.encode("utf-8"))
        logger.debug(f'Telnet connection established with host: %s', self.host)
        return tn_connection
    
    def create_super_user_session(self):

        self.connection.write('sudo su\n'.encode('utf-8'))
        flag = self.login +":"
        self.connection.read_until(flag.encode('utf-8'))
        password = self.password + "\n"
        # Enter password
        self.connection.write(password.encode("utf-8"))
        logger.debug('Super user session created')


    def close(self): 
        self.connection.write(b"exit\n")
        logger.debug(f'Telnet connection closed with host: %s', self.host)
        

    def send_command(self, command: str):
        if 'sudo ' in command:
            self.create_super_user_session()
            filter = (self.login+"#").encode("utf-8")
        else: 
            filter = (self.login+"@").encode("utf-8")
        self.connection.read_until(filter)
        command = command + "\n"
        self.connection.write(command.encode("utf-8"))
        self.log_command_output(command)


    def log_command_output(self, command: str):
        # TODO: process command result
        logger.debug("--------------------Executed commands------------------------")
        logger.debug(f'Command:\n%s',command)        
        output = ""
        if 'sudo ' in command:
            filter = (self.login+"#").encode("utf-8")
        else: 
            filter = (self.login+"@").encode("utf-8")
        while True:                           
            data = self.connection.read_some() # read available data
            if any(x in data for x in [b"\n", b"~$"]):
                output += data.decode("utf-8")
            # check if it is the last line
            if filter in data:
                # remove last line
                output = output[:output.rfind('\n')]
                logger.debug(f'Output:\n%s',output)
                logger.debug("-------------------------------------------------------------")
                break

