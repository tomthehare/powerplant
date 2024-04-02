from logging import Logger

from client.components.config import Config
from client.components.event_client import EventClient
from client.components.fake_web_client import FakeWebClient
from client.components.pump import Pump
from client.components.task_coordinator import TaskCoordinator
from client.components.tasks.valve_close_task import ValveCloseTask
from client.components.tasks.water_queue_task import WaterQueueTask
from client.components.valve import Valve
from client.components.valve_lock import ValveLock
from client.pin_config import PinConfig


class ValveTestOperation:

    def __init__(self, server_url: str, logger: Logger):
        self.server_url = server_url
        self.logger = logger

    def run_operation(self, task_coordinator: TaskCoordinator):
        event_client = EventClient()
        open_duration_seconds = 12

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
            {
                "valve_id": 4,
                "description": "VALVE4",
                "conductivity_threshold": 0.6,
                "watering_delay_seconds": 10,
                "open_duration_seconds": open_duration_seconds,
            },
            {
                "valve_id": 5,
                "description": "VALVE5",
                "conductivity_threshold": 0.6,
                "watering_delay_seconds": 10,
                "open_duration_seconds": open_duration_seconds,
            },
            {
                "valve_id": 6,
                "description": "VALVE6",
                "conductivity_threshold": 0.6,
                "watering_delay_seconds": 10,
                "open_duration_seconds": open_duration_seconds,
            },
            {
                "valve_id": 7,
                "description": "VALVE7",
                "conductivity_threshold": 0.6,
                "watering_delay_seconds": 10,
                "open_duration_seconds": open_duration_seconds,
            },
            {
                "valve_id": 8,
                "description": "VALVE8",
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
        valve4 = Valve(
            4,
            PinConfig.PIN_VALVE_4_POWER,
            config.get_valve_config(4),
            self.logger,
            event_client,
        )
        valve5 = Valve(
            5,
            PinConfig.PIN_VALVE_5_POWER,
            config.get_valve_config(5),
            self.logger,
            event_client,
        )
        valve6 = Valve(
            6,
            PinConfig.PIN_VALVE_6_POWER,
            config.get_valve_config(6),
            self.logger,
            event_client,
        )
        valve7 = Valve(
            7,
            PinConfig.PIN_VALVE_7_POWER,
            config.get_valve_config(7),
            self.logger,
            event_client,
        )
        valve8 = Valve(
            8,
            PinConfig.PIN_VALVE_8_POWER,
            config.get_valve_config(8),
            self.logger,
            event_client,
        )

        valve_lock = ValveLock(self.logger)
        valve_dict = {
            "1": valve1,
            "2": valve2,
            "3": valve3,
            "4": valve4,
            "5": valve5,
            "6": valve6,
            "7": valve7,
            "8": valve8,
        }

        valve_queue = [
            {"valve_id": 1, "open_duration_seconds": open_duration_seconds},
            {"valve_id": 2, "open_duration_seconds": open_duration_seconds},
            {"valve_id": 3, "open_duration_seconds": open_duration_seconds},
            {"valve_id": 4, "open_duration_seconds": open_duration_seconds},
            {"valve_id": 5, "open_duration_seconds": open_duration_seconds},
            {"valve_id": 6, "open_duration_seconds": open_duration_seconds},
            {"valve_id": 7, "open_duration_seconds": open_duration_seconds},
            {"valve_id": 8, "open_duration_seconds": open_duration_seconds},
        ]

        # For testing individual:
        # valve_queue = [
        #   {
        #       'valve_id': 8,
        #       'open_duration_seconds': open_duration_seconds
        #   }
        # ]

        pump = Pump(PinConfig.PIN_PUMP_POWER, self.logger)

        water_queue = WaterQueueTask(
            FakeWebClient(self.server_url, self.logger, valve_queue),
            30,
            valve_lock,
            valve_dict,
            pump,
        )

        task_coordinator.register_task(water_queue)
        task_coordinator.register_task(
            ValveCloseTask(valve1, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve2, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve3, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve4, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve5, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve6, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve7, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve8, valve_lock, config, pump, self.logger)
        )

        task_coordinator.run()
