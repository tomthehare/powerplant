import time
import json
import plotly
import plotly.graph_objects as go
from time_helper import format_timestamp_as_local

class GraphHelper:


    def __init__(self, database_client):
        self.database_client = database_client

    def get_temperature(self, timestamp_start, timestamp_end):
        inside_data_array = self.database_client.read_inside_temperature(timestamp_start, timestamp_end)
        outside_data_array = self.database_client.read_outside_temperature(timestamp_start, timestamp_end)

        inside_dates = [format_timestamp_as_local(a_tuple[0]) for a_tuple in inside_data_array]
        inside_temperatures = [a_tuple[1] for a_tuple in inside_data_array]

        outside_dates = [format_timestamp_as_local(a_tuple[0]) for a_tuple in outside_data_array]
        outside_temperatures = [a_tuple[1] for a_tuple in outside_data_array]

        response = []

        scatter_inside = go.Scatter(
                x=inside_dates,
                y=inside_temperatures,
                name='Inside Temperature',
                line=dict(width=2),
            )

        response.append(scatter_inside)

        scatter_outside = go.Scatter(
                x=outside_dates,
                y=outside_temperatures,
                name='Outside Temperature',
                line=dict(width=2),
            )

        response.append(scatter_outside)


        return json.dumps(
            response,
            cls=plotly.utils.PlotlyJSONEncoder,
        )	
