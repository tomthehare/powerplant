from logging import Logger
import RPi.GPIO as GPIO


class GPIOController:

    _TEST_MODE = False
    _logger: Logger = None

    @classmethod
    def set_test_mode(cls, is_testing: bool, logger: Logger):
        if is_testing:
            cls._TEST_MODE = True
            cls.logger = logger
        else:
            cls._TEST_MODE = False

    @classmethod
    def register_pin(cls, pin: int):
        GPIO.setup(pin, GPIO.OUT)

    @classmethod
    def activate_pin(cls, pin: int):
        if not cls._TEST_MODE:
            GPIO.output(pin, GPIO.HIGH)
        else:
            cls.logger.info("[TESTING] Set GPIO Pin %d to HIGH" % pin)

    @classmethod
    def deactivate_pin(cls, pin: int):
        if not cls._TEST_MODE:
            GPIO.output(pin, GPIO.LOW)
        else:
            cls.logger.info("[TESTING] Set GPIO Pin %d to LOW" % pin)
