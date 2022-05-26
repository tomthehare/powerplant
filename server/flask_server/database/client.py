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
