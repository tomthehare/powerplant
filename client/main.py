import RPi.GPIO as GPIO
import logging
import signal
import sys
import coloredlogs
from components.task_coordinator import TaskCoordinator
from components.web_client import WebClient
from gpio_controller import GPIOController
from operations.attic_fan_test_operation import AtticFanTestOperation
from operations.normal_operation import NormalOperation
from operations.valve_test_operation import ValveTestOperation
from operations.window_test_operation import WindowTestOperation

coloredlogs.install(level="DEBUG", fmt="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()

GPIOController.set_test_mode(False, logger)

SERVER_URLS = ["http://127.0.0.1:8000", "http://192.168.86.47:8000"]

task_coordinator = TaskCoordinator(logger)


def signal_handler(sig, frame):
    print("You pressed Ctrl+C!")
    task_coordinator.shutdown()
    GPIO.cleanup()
    sys.exit(0)


############################
### MAIN EXECUTION BELOW ###
############################
logger.info("Starting up...")
signal.signal(signal.SIGINT, signal_handler)

# use the numbers printed on the guides, not the ones on the board
GPIO.setmode(GPIO.BCM)

logger.info("Finding server address...")
active_server_url = ""
iterations = 0
max_iterations = 5
while active_server_url == "" and iterations < max_iterations:
    iterations = iterations + 1
    for url in SERVER_URLS:
        logger.info("checking for server: %s" % url)
        if WebClient(url, logger).ping_server():
            logging.info("Found an active server at %s" % url)
            active_server_url = url
            break
    time.sleep(5)

if not active_server_url:
    raise Exception("No server url found!")

operation = NormalOperation(active_server_url, logger)
operation.run_operation(task_coordinator)

# operation = WindowTestOperation(active_server_url, logger)
# operation.run_operation()

GPIO.cleanup()
exit(0)
