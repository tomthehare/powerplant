import logging
import sys

class PowerPlantLogger:

    @staticmethod
    def get_logger(log_level: int = logging.DEBUG):
        logger = logging.getLogger('powerplant')
        logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logFormatter)
        logger.setLevel(log_level)
        logger.addHandler(handler)

        return logger