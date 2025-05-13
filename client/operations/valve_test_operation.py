from logging import Logger

from components.tasks.pump_modulation_task import NoOpPumpModulationTask
from components.config import Config
from components.event_client import EventClient
from components.fake_web_client import FakeWebClient
from components.task_coordinator import TaskCoordinator
from components.tasks.valve_close_task import ValveCloseTask
from components.tasks.water_queue_task import WaterQueueTask
from components.valve import Valve
from components.valve_lock import ValveLock
from pin_config import PinConfig


class ValveTestOperation:

    def __init__(self, server_url: str, logger: Logger):
        self.server_url = server_url
        self.logger = logger

    def run_operation(self, task_coordinator: TaskCoordinator):
        event_client = EventClient()
        open_duration_seconds = 60

        configuration = [
            {
                "valve_id": 1,
                "description": "VALVE1",
                "conductivity_threshold": 0.6,
                "watering_delay_seconds": 10,
                "open_duration_seconds": open_duration_seconds,
            },
            {
                "valve_id": 2,
                "description": "VALVE2",
                "conductivity_threshold": 0.6,
                "watering_delay_seconds": 10,
                "open_duration_seconds": open_duration_seconds,
            },
            {
                "valve_id": 3,
                "description": "VALVE3",
                "conductivity_threshold": 0.6,
                "watering_delay_seconds": 10,
                "open_duration_seconds": open_duration_seconds,
            },
        ]

        config = Config()
        config.update_valve_config(configuration)

        valve1 = Valve(
            1,
            PinConfig.PIN_VALVE_1_POWER,
            config.get_valve_config(1),
            self.logger,
            event_client,
        )
        valve2 = Valve(
            2,
            PinConfig.PIN_VALVE_2_POWER,
            config.get_valve_config(2),
            self.logger,
            event_client,
        )
        valve3 = Valve(
            3,
            PinConfig.PIN_VALVE_3_POWER,
            config.get_valve_config(3),
            self.logger,
            event_client,
        )

        valve_lock = ValveLock(self.logger)
        valve_dict = {
            "1": valve1,
            "2": valve2,
            "3": valve3,
        }

        valve_queue = [
            {"valve_id": 1, "open_duration_seconds": open_duration_seconds},
            # {"valve_id": 2, "open_duration_seconds": open_duration_seconds},
            {"valve_id": 3, "open_duration_seconds": open_duration_seconds},
        ]

        no_op_pump_modulation = NoOpPumpModulationTask()

        water_queue = WaterQueueTask(
            self.logger,
            FakeWebClient(self.server_url, self.logger, valve_queue),
            15,
            valve_lock,
            valve_dict,
            no_op_pump_modulation,
            config
        )

        task_coordinator.register_task(water_queue)
        task_coordinator.register_task(
            ValveCloseTask(valve1, valve_lock, config, no_op_pump_modulation, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve2, valve_lock, config, no_op_pump_modulation, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve3, valve_lock, config, no_op_pump_modulation, self.logger)
        )

        task_coordinator.run()
