from database.client import ConnectionWrapper

db_command = """
DROP TABLE ValveCatalog
"""

connection = ConnectionWrapper('powerplant.db')

connection.execute_sql(db_command)

connection.wrap_it_up()
