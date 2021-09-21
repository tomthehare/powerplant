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
            
        if "HeatIndex" not in tables:
            heat_index_table_sql = """
             CREATE TABLE HeatIndex (
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
                Description TEXT
            )
            """
            connection.execute_sql(valve_catalog_table_sql)
            
            valve_insert_sql = """
            INSERT INTO ValveCatalog (ValveID, Description) VALUES (1, 'Initial experiment valve 2021')
            """
            connection.execute_sql(valve_insert_sql)

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

    def insert_temperature(
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
            
    def insert_heat_index(
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
        
    def insert_humidity(
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

    def read_temperature(self, min_seconds, max_seconds):
        sql = """
        SELECT Timestamp, DegreesF 
        FROM Temperature
        WHERE Timestamp >= {min_seconds} AND Timestamp < {max_seconds} 
        """.format(min_seconds=min_seconds, max_seconds=max_seconds)

        connection = ConnectionWrapper(self.database_name)

        try:
            connection.execute_sql(sql)
            results = connection.get_results()
        finally:
            connection.wrap_it_up()

        return results

    
    def read_humidity(self, min_seconds, max_seconds):
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


    def read_heat_index(self, min_seconds, max_seconds):
        sql = """
        SELECT Timestamp, DegreesF 
        FROM HeatIndex
        WHERE Timestamp >= {min_seconds} AND Timestamp < {max_seconds} 
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
