import sqlite3

class DatabaseClient:

    def __init__(self, database_name):
        self.database_name = database_name

    def create_tables_if_not_exist(self):
        sql = """
            SELECT name FROM sqlite_master WHERE type = \'table\'
        """

        connection = ConnectionWrapper(self.database_name)
        connection.execute_sql(sql)

        results = connection.get_results()

        tables = []
        for result in results:
            tables.append(result[0])


        if "Temperature" not in tables:
            temperature_table_sql = """
             CREATE TABLE Temperature (
                    Timestamp INTEGER PRIMARY KEY,
                    DegreesF REAL
                );
            """
            connection.execute_sql(temperature_table_sql)


        if "OutsideTemperature" not in tables:
            temperature_table_sql = """
             CREATE TABLE OutsideTemperature (
                    Timestamp INTEGER PRIMARY KEY,
                    DegreesF REAL
                );
            """

            connection.execute_sql(temperature_table_sql)
            
        if "HeatIndex" not in tables:
            heat_index_table_sql = """
             CREATE TABLE HeatIndex (
                    Timestamp INTEGER PRIMARY KEY,
                    DegreesF REAL
                );
            """

            connection.execute_sql(heat_index_table_sql)

        if "OutsideHeatIndex" not in tables:
            heat_index_table_sql = """
             CREATE TABLE OutsideHeatIndex (
                    Timestamp INTEGER PRIMARY KEY,
                    DegreesF REAL
                );
            """

            connection.execute_sql(heat_index_table_sql)

        if "Humidity" not in tables:
            humidity_table_sql = """
            CREATE TABLE Humidity (
                Timestamp INTEGER PRIMARY KEY,
                Percentage REAL
            )
            """
            connection.execute_sql(humidity_table_sql)

        if "OutsideHumidity" not in tables:
            humidity_table_sql = """
            CREATE TABLE OutsideHumidity (
                Timestamp INTEGER PRIMARY KEY,
                Percentage REAL
            )
            """
            connection.execute_sql(humidity_table_sql)


        if "CpuTemperature" not in tables:
            cpu_temp_table_sql = """
            CREATE TABLE CpuTemperature (
                Timestamp INTEGER PRIMARY KEY,
                DegreesF REAL
            )
            """
            connection.execute_sql(cpu_temp_table_sql)

        if "ValveCatalog" not in tables:
            valve_catalog_table_sql = """
            CREATE TABLE ValveCatalog (
                ValveId INTEGER PRIMARY KEY,
                Description TEXT,
                ConductivityThreshold REAL,
                WateringDelaySeconds INTEGER,
                OpenDurationSeconds INTEGER
            )
            """
            connection.execute_sql(valve_catalog_table_sql)
            
            valve_insert_sql = [
                    "INSERT INTO ValveCatalog (ValveID, Description, ConductivityThreshold, WateringDelaySeconds, OpenDurationSeconds) VALUES (1, 'Valve1', 0.3, 900, 45);", 
                    "INSERT INTO ValveCatalog (ValveID, Description, ConductivityThreshold, WateringDelaySeconds, OpenDurationSeconds) VALUES (2, 'Valve2', 0.3, 900, 45);",
                    "INSERT INTO ValveCatalog (ValveID, Description, ConductivityThreshold, WateringDelaySeconds, OpenDurationSeconds) VALUES (3, 'Valve3', 0.3, 900, 45);",
                    "INSERT INTO ValveCatalog (ValveID, Description, ConductivityThreshold, WateringDelaySeconds, OpenDurationSeconds) VALUES (7, 'Valve7', 0.3, 900, 45);",
                    "INSERT INTO ValveCatalog (ValveID, Description, ConductivityThreshold, WateringDelaySeconds, OpenDurationSeconds) VALUES (8, 'Valve8', 0.3, 900, 45);",
                    "INSERT INTO ValveCatalog (ValveID, Description, ConductivityThreshold, WateringDelaySeconds, OpenDurationSeconds) VALUES (9, 'Valve9', 0.3, 900, 45);"
            ]
            
            for sql in valve_insert_sql:            
                connection.execute_sql(sql)

        if "PlantCatalog" not in tables:
            plant_catalog_table_sql = """
            CREATE TABLE PlantCatalog (
                PlantID INTEGER,
                Tag TEXT,
                Description TEXT
            )
            """
            connection.execute_sql(plant_catalog_table_sql)

        if "ValveOperation" not in tables:
            valve_operation_table_sql = """
            CREATE TABLE ValveOperation (
                Timestamp INTEGER PRIMARY KEY,
                OperationType INTEGER,
                ValveId INTEGER, FOREIGN KEY(ValveId) REFERENCES ValveCatalog(ValveId)
            )
            """
            connection.execute_sql(valve_operation_table_sql)
            
        if "OperationCatalog" not in tables:
            operation_catalog_table_sql = """
            CREATE TABLE OperationCatalog (
                Type INTEGER PRIMARY KEY,
                Description
            )
            """
            connection.execute_sql(operation_catalog_table_sql)
            
            operations_sql = """
            INSERT INTO OperationCatalog(Type, Description) VALUES
            (1, 'Opened'),
            (2, 'Closed')
            """
            
            connection.execute_sql(operations_sql)
            
        if "Logs" not in tables:
            operation_catalog_table_sql = """
            CREATE TABLE Logs (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp INTEGER,
                LogText TEXT               
            )
            """
            connection.execute_sql(operation_catalog_table_sql)

        if "SoilVoltage" not in tables:
            soil_voltage_table_sql = """
            CREATE TABLE SoilVoltage (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp INTEGER,
                PlantTag TEXT,
                Voltage REAL
            )
            """
            connection.execute_sql(soil_voltage_table_sql)

        if "FanEvents" not in tables:
            sql = """
            CREATE TABLE FanEvents (
                EventHash TEXT PRIMARY KEY,
                OnTimestamp INTEGER,
                OffTimestamp INTEGER
            )
            """
            connection.execute_sql(sql)

        if "ValveEvents" not in tables:
            sql = """
            CREATE TABLE ValveEvents (
                EventHash TEXT PRIMARY KEY,
                ValveID INTEGER NOT NULL,
                OpenTimestamp INTEGER,
                ClosedTimestamp INTEGER
            )
            """
            connection.execute_sql(sql)

        if "PowerPlantEvents" not in tables:
            sql = """
            CREATE TABLE PowerPlantEvents (
                EventID TEXT PRIMARY KEY,
                SubjectType TEXT NOT NULL,
                SubjectID TEXT NOT NULL,
                Verb TEXT NOT NULL,
                Timestamp INTEGER NOT NULL
            )
            """
            connection.execute_sql(sql)

        connection.wrap_it_up()

    def insert_log(
        self,
        timestamp,
        log_text
    ):
        sql = f"""
        INSERT INTO Logs (Timestamp, LogText)
        VALUES ({timestamp}, '{log_text}')
        """
        
        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()

    def insert_inside_temperature(
        self,
        timestamp,
        degrees_f
    ):
        sql = f"""
        INSERT INTO Temperature (Timestamp, DegreesF)
        VALUES ({timestamp}, {degrees_f})
        """

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()


    def insert_outside_temperature(
        self,
        timestamp,
        degrees_f
    ):
        sql = f"""
        INSERT INTO OutsideTemperature (Timestamp, DegreesF)
        VALUES ({timestamp}, {degrees_f})
        """

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()
            
    def insert_outside_heat_index(
        self,
        timestamp,
        degrees_f
    ):
        sql = f"""
        INSERT INTO OutsideHeatIndex (Timestamp, DegreesF)
        VALUES ({timestamp}, {degrees_f})
        """

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()


    def insert_inside_heat_index(
        self,
        timestamp,
        degrees_f
    ):
        sql = f"""
        INSERT INTO HeatIndex (Timestamp, DegreesF)
        VALUES ({timestamp}, {degrees_f})
        """

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()

    def insert_outside_humidity(
        self,
        timestamp,
        percentage
    ):
        sql = f"""
        INSERT INTO OutsideHumidity (Timestamp, Percentage)
        VALUES ({timestamp}, {percentage})
        """

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()


    def insert_inside_humidity(
        self,
        timestamp,
        percentage
    ):
        sql = f"""
        INSERT INTO Humidity (Timestamp, Percentage)
        VALUES ({timestamp}, {percentage})
        """

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()
            
    def insert_cpu_temperature(
        self,
        timestamp,
        degrees_f
    ):
        sql = f"""
        INSERT INTO CpuTemperature (Timestamp, DegreesF)
        VALUES ({timestamp}, {degrees_f})
        """

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()
            
    def insert_valve_operation(
        self,
        timestamp,
        valve_id,
        operation_type
    ):
        sql = f"""
        INSERT INTO ValveOperation (Timestamp, ValveId, OperationType)
        VALUES ({timestamp}, {valve_id}, {operation_type})
        """

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()

    def insert_soil_voltage(
        self,
        timestamp,
        plant_tag,
        soil_voltage
    ):
        sql = f"""
        INSERT INTO SoilVoltage (Timestamp, PlantTag, Voltage)
        VALUES ({timestamp}, '{plant_tag}', {soil_voltage})
        """

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()

    def read_outside_temperature(self, min_seconds, max_seconds):
        sql = """
        SELECT Timestamp, DegreesF 
        FROM OutsideTemperature
        WHERE Timestamp >= {min_seconds} AND Timestamp < {max_seconds} 
        ORDER BY Timestamp
        """.format(min_seconds=min_seconds, max_seconds=max_seconds)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return results


    def read_inside_temperature(self, min_seconds, max_seconds):
        sql = """
        SELECT Timestamp, DegreesF 
        FROM Temperature
        WHERE Timestamp >= {min_seconds} AND Timestamp < {max_seconds} 
        ORDER BY Timestamp
        """.format(min_seconds=min_seconds, max_seconds=max_seconds)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return results


    def read_outside_humidity(self, min_seconds, max_seconds):
        sql = """
        SELECT Timestamp, Percentage 
        FROM OutsideHumidity
        WHERE Timestamp >= {min_seconds} AND Timestamp < {max_seconds} 
        """.format(min_seconds=min_seconds, max_seconds=max_seconds)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return results


    def read_inside_humidity(self, min_seconds, max_seconds):
        sql = """
        SELECT Timestamp, Percentage 
        FROM Humidity
        WHERE Timestamp >= {min_seconds} AND Timestamp < {max_seconds} 
        """.format(min_seconds=min_seconds, max_seconds=max_seconds)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return results


    def read_outside_heat_index(self, min_seconds, max_seconds):
        sql = """
        SELECT Timestamp, DegreesF 
        FROM OutsideHeatIndex
        WHERE Timestamp >= {min_seconds} AND Timestamp < {max_seconds} 
        """.format(min_seconds=min_seconds, max_seconds=max_seconds)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return results


    def read_inside_heat_index(self, min_seconds, max_seconds):
        sql = """
        SELECT Timestamp, DegreesF 
        FROM HeatIndex
        WHERE Timestamp >= {min_seconds} AND Timestamp < {max_seconds} 
        ORDER BY Timestamp
        """.format(min_seconds=min_seconds, max_seconds=max_seconds)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return results


    def read_logs(self, min_seconds, max_seconds):
        sql = """
        SELECT Timestamp, LogText 
        FROM Logs
        WHERE Timestamp >= {min_seconds} AND Timestamp < {max_seconds} 
        """.format(min_seconds=min_seconds, max_seconds=max_seconds)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return results

    def read_most_recent_plant_voltage(self, plant_tag):
        sql = """
        SELECT Timestamp, Voltage
        FROM SoilVoltage 
        WHERE PlantTag = '{plant_tag}'
        ORDER BY Timestamp DESC
        LIMIT 1
        """.format(plant_tag=plant_tag)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return results

    def read_last_valve_opening(self, plant_tag):
        sql = """
        SELECT ValveOperation.ValveId, Timestamp 
        FROM ValveOperation
        INNER JOIN JoinPlantValveGroup ON JoinPlantValveGroup.ValveID = ValveOperation.ValveId
        INNER JOIN PlantCatalog ON PlantCatalog.PlantID = JoinPlantValveGroup.PlantID
        WHERE OperationType = 1 AND PlantCatalog.PlantTag = '{plant_tag}'
        ORDER BY Timestamp DESC
        LIMIT 1
        """.format(plant_tag=plant_tag)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return results

    def get_valve_config(self):
        sql = """
        SELECT ValveId, Description, ConductivityThreshold, WateringDelaySeconds, OpenDurationSeconds
        FROM ValveCatalog
        ORDER BY ValveId ASC
        """

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()


        # Let's format the dictionary a bit better so it has proper keys on it
        return_list = []
        for result in results:
            return_list.append(
                {
                    'valve_id': result[0],
                    'description': result[1],
                    'conductivity_threshold': result[2],
                    'watering_delay_seconds': result[3],
                    'open_duration_seconds': result[4],
                }
            )

        return return_list

    def fan_event_exists(self, sync_hash):
        sql = """
        SELECT EventHash FROM FanEvents WHERE EventHash = '{event_hash}'
        """.format(event_hash=sync_hash)


        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return results != []

    def insert_fan_on_event(self, timestamp, sync_hash):
        sql = """
        INSERT INTO FanEvents (EventHash, OnTimestamp, OffTimestamp)
        VALUES ('{event_hash}', {on_timestamp}, NULL)
        """.format(event_hash=sync_hash, on_timestamp=timestamp)


        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()

    def update_fan_off_event(self, timestamp, sync_hash):
        sql = """
        UPDATE FanEvents SET OffTimestamp = {off_timestamp} WHERE EventHash = '{sync_hash}'
        """.format(off_timestamp=timestamp, sync_hash=sync_hash)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()


    def valve_event_exists(self, sync_hash):
        sql = """
        SELECT EventHash FROM ValveEvents WHERE EventHash = '{event_hash}'
        """.format(event_hash=sync_hash)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return results != []

    def get_last_valve_event(self, valve_id):
        sql = """
        SELECT OpenTimestamp, ClosedTimestamp, vc.Description
        FROM ValveEvents ve
        INNER JOIN ValveCatalog vc ON vc.ValveID = ve.ValveID 
        WHERE ve.ValveID = {valve_id}
        ORDER BY OpenTimestamp DESC
        LIMIT 1;
        """.format(valve_id=valve_id)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()

            if results:
                return {
                    'name': results[0][2],
                    'opened': results[0][0],
                    'closed': results[0][1]
                }
            else:
                return None
        finally:
            connection.wrap_it_up()

        return None

    def insert_valve_open_event(self, valve_id, timestamp, sync_hash):
        sql = """
        INSERT INTO ValveEvents (EventHash, ValveID, OpenTimestamp, ClosedTimestamp)
        VALUES ('{event_hash}', {valve_id}, {on_timestamp}, NULL)
        """.format(event_hash=sync_hash, valve_id=valve_id, on_timestamp=timestamp)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()

    def update_valve_close_event(self, timestamp, sync_hash):
        sql = """
        UPDATE ValveEvents SET ClosedTimestamp = {closed_timestamp} WHERE EventHash = '{sync_hash}'
        """.format(closed_timestamp=timestamp, sync_hash=sync_hash)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()

    def read_fan_data(self, ts_start, ts_end):
        sql = """
        SELECT EventHash, OnTimestamp, OffTimestamp
        FROM FanEvents
        WHERE (OnTimestamp < {ts_end} AND OffTimestamp > {ts_start}) 
        OR (OnTimestamp <= {ts_start} AND OffTimestamp > {ts_start} AND OffTimestamp <= {ts_end})
        OR (OnTimestamp > {ts_start} AND OffTimestamp > {ts_start} AND OffTimestamp > {ts_end}) 
        OR (OnTimestamp > {ts_start} AND OffTimestamp IS NULL)
        ORDER BY OnTimestamp
        """.format(ts_start=ts_start, ts_end=ts_end)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return results

    def get_powerplant_events(self, ts_start: int, ts_end: int):
        sql = """
        SELECT
            EventID,
            SubjectType,
            SubjectID,
            Verb,
            Timestamp 
        FROM PowerPlantEvents
        WHERE Timestamp >= {ts_start}
          AND Timestamp <= {ts_end}
        ORDER BY TimeStamp
        """.format(ts_start=ts_start, ts_end=ts_end)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return [
            {
                "event_id": a[0],
                "subject_type": a[1],
                "subject_id": a[2],
                "verb": a[3],
                "timestamp": int(a[4])
            }
            for a in results
        ]

    def insert_powerplant_event(self, event_id: str, subject_type: str, subject_id: str, verb: str, timestamp: int):
        sql = """
        INSERT INTO PowerPlantEvents (EventID, SubjectType, SubjectID, Verb, Timestamp) VALUES ('{event_id}', '{subject_type}', '{subject_id}', '{verb}', {timestamp});
        """.format(event_id=event_id, subject_id=subject_id, subject_type=subject_type, verb=verb, timestamp=timestamp)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
        finally:
            connection.wrap_it_up()

class ConnectionWrapper:

    _cursor = None
    _connection = None
    _last_rows = None

    def __init__(self, database_name):
        self._connection = sqlite3.connect(database_name)
        self._cursor = self._connection.cursor()

    def execute_sql(self, sql: str):

        if self._cursor is not None:
            self._cursor.execute(sql)

        if self._connection is not None:
            self._connection.commit()

    def get_results(self):
        return self._cursor.fetchall()

    def wrap_it_up(self):
        self._cursor.close()
        self._connection.close()
