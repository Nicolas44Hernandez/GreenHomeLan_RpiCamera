import logging
import subprocess
from server.common import ServerCameraException, ErrorCode

logger = logging.getLogger(__name__)


class IpDiscoveryService:
    """Ip discovery service"""

    def reload_tables():
        """Make a brodcast ping to reload arp tables"""
        brodcast_ping_process = subprocess.Popen(
            ["nmap", "-sn", "192.168.1.0/24"], stdout=subprocess.PIPE
        )
        brodcast_ping_process.wait()
        if brodcast_ping_process.returncode != 0:
            logger.error(f"Error in brodcast ping")
            raise ServerCameraException(ErrorCode.IP_DISCOVERY_BRODCAST_PING_ERROR)
        logger.info(f"Brodcast ping ok")

    def get_ip_addr(mac: str) -> str:
        """Get ip address from mac"""

        # reload arp tables
        IpDiscoveryService.reload_tables()
        # ip neighbor | greep -i {mac}
        try:
            cmd1 = subprocess.Popen(["ip", "neighbor"], stdout=subprocess.PIPE)
            cmd2 = subprocess.check_output(["grep", "-i", mac], stdin=cmd1.stdout)
            station_ip = cmd2.decode().split(" ")[0]
        except:
            logger.error(f"Station {mac} not connected")
            raise ServerCameraException(ErrorCode.IP_DISCOVERY_UNKNOWN_STATION)
        logger.info(f"Station {mac} connected in {station_ip}")
        return station_ip
