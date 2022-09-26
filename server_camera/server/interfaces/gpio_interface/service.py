"""
GPIO interface service
"""
import logging
from gpiozero import Button, MotionSensor

logger = logging.getLogger(__name__)


class GpioButtonInterface:
    """Service class for RPI Button GPIO"""

    button_pin: int
    button: Button
    callback_function: callable

    def __init__(self, button_pin: int, callback_function: callable):

        logger.info(f"Creating RPI GPIO Button interface:")
        logger.info(f"button_pin: {button_pin}")
        logger.info(f"callback_function: {callback_function}")

        self.button_pin = button_pin

        # setup
        self.button = Button(self.button_pin)
        self.button.when_pressed = callback_function


class GpioMotionSensorInterface:
    """Service class for RPI Button GPIO"""

    sensor_pin: int
    motion_sensor: MotionSensor
    callback_function: callable

    def __init__(self, sensor_pin: int, callback_function: callable):

        logger.info(f"Creating RPI GPIO MotionSensor interface:")
        logger.info(f"button_pin: {sensor_pin}")
        logger.info(f"callback_function: {callback_function}")

        self.sensor_pin = sensor_pin

        # setup
        self.motion_sensor = MotionSensor(self.sensor_pin)
        # sensor output  is inverted
        self.motion_sensor.when_no_motion = callback_function
