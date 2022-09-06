"""
GPIO interface service
"""
import logging
import RPi.GPIO as GPIO


logger = logging.getLogger(__name__)


class GpioInterface:
    """Service class for RPI GPIO"""

    doorbell_button: int
    callback_function: callable

    def __init__(self, doorbell_button: int, callback_function: callable):

        logger.info(f"Creating RPI GPIO interface:")
        logger.info(f"doorbell_button: {doorbell_button}")
        logger.info(f"callback_function: {callback_function}")

        self.doorbell_button = doorbell_button

        # setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.doorbell_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.doorbell_button, GPIO.RISING, callback=callback_function, bouncetime=300
        )
