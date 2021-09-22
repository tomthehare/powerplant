import time
import json
import plotly
import plotly.graph_objects as go
from time_helper import format_timestamp_as_local

class GraphHelper:


    def __init__(self, database_client):
        self.database_client = database_client

    def get_temperature(self, timestamp_start, timestamp_end):
        data_array = self.database_client.read_temperature(timestamp_start, timestamp_end)

        dates = [format_timestamp_as_local(a_tuple[0]) for a_tuple in data_array]
        temperatures = [a_tuple[1] for a_tuple in data_array]

        response = []

        scatter = go.Scatter(
                x=dates,
                y=temperatures,
                name='Temperature',
                line=dict(width=2),
            )

        response.append(scatter)

        return json.dumps(
            response,
            cls=plotly.utils.PlotlyJSONEncoder,
        )	
