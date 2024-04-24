import RPi.GPIO as GPIO
import logging
import signal
import sys
import coloredlogs
from components.task_coordinator import TaskCoordinator
from operations.normal_operation import NormalOperation

coloredlogs.install(level="DEBUG", fmt="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()


SERVER_URL = "http://192.168.86.47:8000"

task_coordinator = TaskCoordinator()


def signal_handler(sig, frame):
    print("You pressed Ctrl+C!")
    task_coordinator.shutdown()
    GPIO.cleanup()
    sys.exit(0)


############################
### MAIN EXECUTION BELOW ###
############################
logging.info("Starting up...")
signal.signal(signal.SIGINT, signal_handler)

# use the numbers printed on the guides, not the ones on the board
GPIO.setmode(GPIO.BCM)

operation = NormalOperation(SERVER_URL, logger)
operation.run_operation(task_coordinator)

GPIO.cleanup()
exit(0)
