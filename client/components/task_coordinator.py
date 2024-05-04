import time
import sys
import traceback
import os
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


class TaskCoordinator:

    def __init__(self, logger: logging.Logger):
        self.tasks = []
        self.enabled = True
        self.logger = logger

    def register_task(self, task):
        self.tasks.append(task)
        self.logger.info("Registered %s" % str(task))

    def run(self):
        while True:
            for task in self.tasks:
                try:
                    if self.enabled:
                        task.run()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    logging.error(e)
                    print(exc_type, fname, exc_tb.tb_lineno)
                    traceback.print_exc()

            time.sleep(0.5)

    def shutdown(self):
        self.enabled = False

        for task in self.tasks:
            if hasattr(task, "shutdown") and callable(getattr(task, "shutdown")):
                task.shutdown()
