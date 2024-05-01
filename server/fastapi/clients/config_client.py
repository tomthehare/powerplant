import json
import os
import shutil
from logging import Logger

from fastapi import HTTPException

from models.config import Config

CONFIG_LOCATION_DEFAULT = "powerplant-config.json"
CONFIG_LOCATION_EMPTY = "config/empty-config.json"

class ConfigClient:
    def __init__(self, logger: Logger):
        self.logger = logger

    def get_config_file_location(self) -> str:
        return CONFIG_LOCATION_DEFAULT

    def ensure_config_exists(self):
        file_location = self.get_config_file_location()
        if not os.path.exists(file_location):
            shutil.copyfile(CONFIG_LOCATION_EMPTY, file_location)

    def get_config(self) -> Config:
        file_path = self.get_config_file_location()
        if os.path.exists(file_path):
            return Config.parse_file(file_path)

        msg = 'Config file does not exist: %s' % self.get_config_file_location()
        self.logger.error(msg)
        raise HTTPException(status_code=500, detail=msg)

    def set_config(self, config: Config):
        with open(self.get_config_file_location(), 'w') as f:
            f.write(config.model_dump_json(indent=2))
