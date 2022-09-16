""" Server camera errors """

from enum import Enum


class ErrorCode(Enum):
    """Enumerate which gather all data about possible errors"""

    # Please enrich this enumeration in order to handle other kind of errors
    UNEXPECTED_ERROR = (0, 500, "Unexpected error occurs")
    THREAD_NODE_NOT_CONFIGURED = (1, 400, "Thread node hasnt been configured yet")
    WIFI_THREAD_COMMANDS_FILE_ERROR = (
        2,
        500,
        "Error in wifi thread commands load, check commands file",
    )
    IP_DISCOVERY_BRODCAST_PING_ERROR = (3, 500, "Error in brodcast ping for ip discovery")
    IP_DISCOVERY_UNKNOWN_STATION = (4, 500, "Error in ip discovery statiopn unknown")

    # pylint: disable=unused-argument
    def __new__(cls, *args, **kwds):
        """Custom new in order to initialize properties"""
        obj = object.__new__(cls)
        obj._value_ = args[0]
        obj._http_code_ = args[1]
        obj._message_ = args[2]
        return obj

    @property
    def http_code(self):
        """The http code corresponding to the error"""
        return self._http_code_

    @property
    def message(self):
        """The message corresponding to the error"""
        return self._message_
