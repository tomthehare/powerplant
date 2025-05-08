import os.path
from logging import Logger

from fastapi.middleware.cors import CORSMiddleware
from clients.config_client import ConfigClient
from clients.water_queue_client import WaterQueueClient
from database.client import DatabaseClient
from payload_builder import PayloadBuilder
from utilities.power_plant_logger import PowerPlantLogger
from fastapi import FastAPI


class Bootstrap:
    def __init__(self):
        self.app: FastAPI
        self.db_client: DatabaseClient
        self.logger: Logger
        self.payload_builder: PayloadBuilder

    def bootstrap_app(self):
        self.app = FastAPI()
        self.define_cross_origin_resource_sharing_policy()

        db_client = DatabaseClient("powerplant.db")
        db_client.create_tables_if_not_exist()
        self.db_client = db_client

        self.logger = PowerPlantLogger.get_logger()

        self.payload_builder = PayloadBuilder(self.logger, db_client)

        ConfigClient(self.logger).ensure_config_exists()

        WaterQueueClient().ensure_water_queue_exists()

    def define_cross_origin_resource_sharing_policy(self):
        allowed_origins = ["http://localhost:5173", "http://192.168.86.172:5173", "http://71.184.132.189/:1"]

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )
