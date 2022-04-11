import time
import json
import plotly
import math
import plotly.graph_objects as go
from time_helper import format_timestamp_as_local, format_timestamp_as_hour_time

class GraphHelper:


    def __init__(self, database_client):
        self.database_client = database_client
        
    def _aggregate_to_minutes(self, dataset):
        agg_set = []
        
        current_minute = None
        current_set = []
        for timestamp, temp in dataset:
            if current_minute is None:
                current_minute = math.floor(timestamp / 60) # minutes since epoch
            
            this_minute = math.floor(timestamp / 60)
            
            if this_minute != current_minute:
                agg_set.append(((current_minute * 60), self._get_avg_for_temp_set(current_set)))
                current_set = []
                current_minute = this_minute
            
            current_set.append(temp)
        
        agg_set.append(((current_minute * 60), self._get_avg_for_temp_set(current_set)))
        
        return agg_set
                
    def _get_avg_for_temp_set(self, temp_set):
        if len(temp_set) == 0:
            return 0
        
        total = 0
        for temp in temp_set:
            total = total + temp
        
        return total / len(temp_set)

    def snap_to_5_min_buckets(self, ts_start, ts_end, data):
        starting_number = ts_start - (ts_start % 300)

        the_range = range(starting_number, ts_end, 300)
        the_dict = {}
        for number in the_range:
            the_dict[number] = []

        for ts, temp in data:
            the_dict[ts - (ts % 300)].append(temp)

        for key in the_dict.keys():
            if len(the_dict[key]) > 0:
                the_dict[key] = self._get_avg_for_temp_set(the_dict[key])
            else:
                the_dict[key] = None

        return the_dict

                

    def get_temperature(self, timestamp_start, timestamp_end):
        inside_data_array = self.database_client.read_inside_temperature(timestamp_start, timestamp_end)
        outside_data_array = self.database_client.read_outside_temperature(timestamp_start, timestamp_end)

        snapped_inside = self.snap_to_5_min_buckets(timestamp_start, timestamp_end, inside_data_array)
        snapped_outside = self.snap_to_5_min_buckets(timestamp_start, timestamp_end, outside_data_array)

        inside_dates = list(snapped_inside.keys())
        inside_temperatures = list(snapped_inside.values())

        outside_dates = list(snapped_outside.keys())
        outside_temperatures = list(snapped_outside.values())

        inside_dates = [format_timestamp_as_hour_time(ts) for ts in inside_dates]
        outside_dates = [format_timestamp_as_hour_time(ts) for ts in outside_dates]

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

        freezing_numbers = []
        for date_placeholder in inside_dates:
            freezing_numbers.append(32)

        freezing_line = go.Scatter(
                x=inside_dates,
                y=freezing_numbers,
                name='Freezing Brr',
                line=dict(width=2, color="#ff0000")
        )

        response.append(freezing_line)

        return json.dumps(
            response,
            cls=plotly.utils.PlotlyJSONEncoder,
        )	
