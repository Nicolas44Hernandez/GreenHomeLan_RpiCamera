"""
GPIO interface service
"""
import logging
from gpiozero import Button

logger = logging.getLogger(__name__)


class GpioInterface:
    """Service class for RPI GPIO"""

    doorbell_button_pin: int
    doorbell_button: Button
    callback_function: callable

    def __init__(self, doorbell_button_pin: int, callback_function: callable):

        logger.info(f"Creating RPI GPIO interface:")
        logger.info(f"doorbell_button_pin: {doorbell_button_pin}")
        logger.info(f"callback_function: {callback_function}")

        self.doorbell_button_pin = doorbell_button_pin

        # setup
        self.doorbell_button = Button(self.doorbell_button_pin)
        self.doorbell_button.when_pressed = callback_function
