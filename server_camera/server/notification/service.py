import logging
from server.managers.mqtt_manager import mqtt_manager_service
from server.managers.thread_manager import thread_manager_service
from server.managers.wifi_connection_manager import wifi_connection_manager_service
from flask import Flask

logger = logging.getLogger(__name__)


class AlarmNotifier:
    """Manager for AlarmNotifier"""

    mqtt_alarm_notif_topic: str

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize AlarmNotifier"""
        if app is not None:
            logger.info("initializing the AlarmNotifier")
            self.mqtt_alarm_notif_topic = app.config["MQTT_ALARM_NOTIFICATION_TOPIC"]

    def notify_alarm(self, alarm_type: str, msg: str):
        logger.info(f"Sending alarm notification alarm:{alarm_type} msg:{msg}")
        """Notify alarm to orchestrator"""
        # TODO: uncomment for working via wifi MQTT
        # if wifi_connection_manager_service.connected:
        #     return self.notify_mqtt_alarm(alarm_type=alarm_type, msg=msg)
        # else:
        return self.notify_thread_alarm(alarm_type=alarm_type)

    def notify_mqtt_alarm(self, alarm_type: str, msg: str) -> bool:
        """Send MQTT message to notify alarm"""
        logger.info(f"Sending notification via MQTT")

        alarm_data = {"type": alarm_type, "msg": msg}

        if mqtt_manager_service.publish_message(
            topic=self.mqtt_alarm_notif_topic, message=alarm_data
        ):
            logger.info(f"Alarm published to MQTT topic {self.mqtt_alarm_notif_topic}")
            logger.info(f"Network info: {alarm_data}")
            return True
        else:
            logger.error(
                "Impossible to publish alarm to MQTT topic {self.mqtt_alarm_notif_topic}"
            )
            return False

    def notify_thread_alarm(self, alarm_type: str) -> bool:
        """Send Thread message to notify alarm"""
        logger.info(f"Sending notification via Thread")

        if alarm_type == "doorbell":
            data_to_send = f"al_cam_db"
        elif alarm_type == "presence":
            data_to_send = f"al_cam_pd"
        else:
            return False
        return thread_manager_service.send_thread_message_to_border_router(data_to_send)


notification_service: AlarmNotifier = AlarmNotifier()
""" AlarmNotifier service singleton"""
