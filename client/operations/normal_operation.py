from logging import Logger

from components.config import Config
from components.event_client import EventClient
from components.pump import Pump
from components.task_coordinator import TaskCoordinator
from components.tasks.attic_fan_task import AtticFanTask
from components.tasks.config_sync_task import ConfigSyncTask
from components.tasks.event_sending_task import EventSendingTask
from components.tasks.temp_humid_log_task import TempHumidLogTask
from components.tasks.valve_close_task import ValveCloseTask
from components.tasks.water_plants_task import WaterPlantsTask
from components.tasks.water_queue_task import WaterQueueTask
from components.temp_humid_sensor import TempHumidSensor
from components.time_observer import TimeObserver
from components.time_observer_test import TimeObserverTest
from components.valve import Valve
from components.valve_lock import ValveLock
from components.web_client import WebClient
from components.window import Window
from components.windows_group import WindowsGroup
from pin_config import PinConfig
from window_config import (
    WINDOW_EAST,
    WINDOW_NORTH,
    WINDOW_SOUTH_EAST,
    WINDOW_SOUTH_WEST,
    get_window_config,
)


class NormalOperation:
    def __init__(self, server_url: str, logger: Logger):
        if not server_url:
            raise Exception("Empty server url given.")

        self.server_url = server_url
        self.logger = logger

    def run_operation(self, task_coordinator: TaskCoordinator):
        event_client = EventClient()

        # time_observer = TimeObserver()
        time_observer = TimeObserverTest(self.logger)

        temp_humid_inside = TempHumidSensor(
            PinConfig.PIN_TEMP_HUMIDITY_INSIDE, self.logger, "inside"
        )
        # temp_humid_outside = TempHumidSensor(PIN_TEMP_HUMIDITY_OUTSIDE, self.logger, "outside")
        web_client = WebClient(self.server_url, self.logger)

        config = Config()

        config_sync_task = ConfigSyncTask(
            TimeObserver.FIFTEEN_MINUTES, web_client, config, self.logger
        )

        # Grab initial settings for valves
        config_sync_task.run()

        valve_lock = ValveLock(self.logger)
        valve_1 = Valve(
            1,
            PinConfig.PIN_VALVE_1_POWER,
            config.get_valve_config(1),
            self.logger,
            event_client,
        )
        valve_2 = Valve(
            2,
            PinConfig.PIN_VALVE_2_POWER,
            config.get_valve_config(2),
            self.logger,
            event_client,
        )
        valve_3 = Valve(
            3,
            PinConfig.PIN_VALVE_3_POWER,
            config.get_valve_config(3),
            self.logger,
            event_client,
        )
        valve_4 = Valve(
            4,
            PinConfig.PIN_VALVE_4_POWER,
            config.get_valve_config(4),
            self.logger,
            event_client,
        )
        valve_5 = Valve(
            5,
            PinConfig.PIN_VALVE_5_POWER,
            config.get_valve_config(5),
            self.logger,
            event_client,
        )
        valve_6 = Valve(
            6,
            PinConfig.PIN_VALVE_6_POWER,
            config.get_valve_config(6),
            self.logger,
            event_client,
        )
        valve_7 = Valve(
            7,
            PinConfig.PIN_VALVE_7_POWER,
            config.get_valve_config(7),
            self.logger,
            event_client,
        )
        valve_8 = Valve(
            8,
            PinConfig.PIN_VALVE_8_POWER,
            config.get_valve_config(8),
            self.logger,
            event_client,
        )

        valve_dict = {
            "1": valve_1,
            "2": valve_2,
            "3": valve_3,
            "4": valve_4,
            "5": valve_5,
            "6": valve_6,
            "7": valve_7,
            "8": valve_8,
        }

        watering_schedule = [
            {"hour": 7, "water_every_days": 1},
        ]

        pump = Pump(PinConfig.PIN_PUMP_POWER, self.logger)

        window_se = Window(
            get_window_config(WINDOW_SOUTH_EAST),
            self.logger,
        )

        window_n = Window(
            get_window_config(WINDOW_NORTH),
            self.logger,
        )
        window_sw = Window(
            get_window_config(WINDOW_SOUTH_WEST),
            self.logger,
        )
        window_e = Window(
            get_window_config(WINDOW_EAST),
            self.logger,
        )
        windows_group = WindowsGroup(
            [window_se, window_n, window_sw, window_e], self.logger
        )

        # Make sure the windows are closed before doing anything else on start up.
        windows_group.close()

        task_coordinator.register_task(config_sync_task)
        task_coordinator.register_task(
            TempHumidLogTask(
                TimeObserver.FIVE_MINUTES,
                temp_humid_inside,
                self.server_url + "/weather-samples",
                web_client,
                "inside",
                self.logger,
            )
        )
        task_coordinator.register_task(
            AtticFanTask(
                60,
                PinConfig.PIN_FAN_POWER,
                temp_humid_inside,
                config,
                windows_group,
                self.logger,
                event_client,
            )
        )
        # task_coordinator.register_task(TempHumidLogTask(FIVE_MINUTES, temp_humid_outside, self.server_url + '/weather-samples', web_client, 'outside', self.logger))
        task_coordinator.register_task(
            WaterPlantsTask(
                TimeObserver.TEN_MINUTES, web_client, watering_schedule, self.logger
            )
        )
        task_coordinator.register_task(
            WaterQueueTask(web_client, 30, valve_lock, valve_dict, pump)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve_1, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve_2, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve_3, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve_4, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve_5, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve_6, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve_7, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            ValveCloseTask(valve_8, valve_lock, config, pump, self.logger)
        )
        task_coordinator.register_task(
            EventSendingTask(
                5, web_client, event_client, self.logger, 5, time_observer=time_observer
            )
        )

        ## Check every 30 seconds to run the circ fans  for 90 seconds every 10 minutes:
        # task_coordinator.register_task(CirculatorFansTask(30, PIN_CIRC_FAN_POWER, TEN_MINUTES, 90))

        task_coordinator.run()
