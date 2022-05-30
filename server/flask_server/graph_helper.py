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

    def get_date_x_axis(self, ts_start, ts_end, empty_value):
        starting_number = ts_start - (ts_start % 300)

        the_range = range(starting_number, ts_end, 300)
        the_dict = {}
        for number in the_range:
            the_dict[number] = [] if isinstance(empty_value, list) else 0

        return the_dict

    def snap_to_5_min_buckets(self, ts_start, ts_end, data):
        the_dict = self.get_date_x_axis(ts_start, ts_end, [])

        for ts, temp in data:
            the_dict[ts - (ts % 300)].append(temp)

        for key in the_dict.keys():
            if len(the_dict[key]) > 0:
                the_dict[key] = self._get_avg_for_temp_set(the_dict[key])
            else:
                the_dict[key] = None

        return the_dict
     
    def get_fan_data(self, timestamp_start, timestamp_end):
        dates_dict = self.get_date_x_axis(timestamp_start, timestamp_end, 0)

        fan_data = self.database_client.read_fan_data(timestamp_start, timestamp_end)
        
        for (event_hash, ts_on, ts_off) in fan_data:
            round_down_to_minute = ts_on - (ts_on % 60)

            working_minute = round_down_to_minute
            while working_minute <= ts_off:
                # Find the bucket that corresponds to this minute in our dates dict
                for key in dates_dict.keys():
                    # See if it falls within the 5 minutes
                    if working_minute >= key and working_minute < (key + 300):
                        dates_dict[key] = dates_dict[key] + 1
                        break

                working_minute = working_minute + 60

        #for key in dates_dict.keys():
        #    if dates_dict[key] == 0:
        #        dates_dict[key] = None
        
        dates = list(dates_dict.keys())
        fan_minutes = list(dates_dict.values())

        dates = [format_timestamp_as_hour_time(ts) for ts in dates]

        response = []

        bar_chart = go.Bar(
                x=dates,
                y=fan_minutes,
                #line=dict(width=2),
            )

        response.append(bar_chart)

        return response

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
