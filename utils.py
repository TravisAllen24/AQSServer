import datetime
import csv
from typing import Any
from contextlib import suppress

### Formatting helpers ###
def format_value(value: Any, precision: int = 0) -> str | int | float:
    """Format the value or return '-' if None."""
    if value is None:
        return "-"

    if isinstance(value, str):
        for parse in (int, float):
            with suppress(ValueError):
                return round(parse(value), precision)
        return value

    if isinstance(value, (int, float)):
        return round(value, precision)

    return str(value)


def get_relevant_data(data_list, time_duration, dts):
    """Filter data based on the specified time duration."""
    now = datetime.datetime.now()
    start_time = now - delta_time(time_duration)
    start_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    relevant_time = []
    relevant_data = []
    for dt, data in zip(dts, data_list):
        if dt >= start_str:
            relevant_time.append(dt)
            relevant_data.append(data)

    return relevant_time, relevant_data


def clean_data(data):
    data = data.replace('\n', '').replace('\r', '').split(',')

    if len(data) != 13 or data[0] != "$AQS":
        return None

    return data[1:]

###### Time helpers ######
def convert_time(time):
    """Convert a string time to a datetime object."""
    return datetime.datetime.fromisoformat(time)


def delta_time(time_duration):
    """Return a timedelta object based on the time duration string."""
    delta = {"Hour": datetime.timedelta(hours=1),
             "Day": datetime.timedelta(days=1),
             "Week": datetime.timedelta(days=7),
             "Month": datetime.timedelta(days=30),
             "Max": datetime.timedelta(days=365)
             }

    return delta.get(time_duration, delta["Max"])


###### Plotting helpers ######
def get_y_label(data_type):
    """Return the appropriate y-axis label based on the data type."""
    y_labels = {"T": 'Temperature (C)',
                "RH": "Relative Humidity (%)",
                "DP": "Dew Point (C)",
                "CO2": "CO2 (ppm)",
                "VOC": "VOC Index",
                "NOX": "NOX Index",
                "PM": "PM (μg/m³)"
    }

    return y_labels.get(data_type, y_labels["T"])


def aggregate_data_avg(data, n=500):
    if len(data) <= n:
        return data
    n = len(data) // n
    return [
        sum(float(v) for v in data[i:i+n] if v != '-') / max(sum(1 for v in data[i:i+n] if v != '-'), 1)
        for i in range(0, len(data), n)
    ]


def aggregate_data_max(data_list, n=120):
    """Aggregate a list of data into n data points based on the specified time duration to reduce computation."""
    if len(data_list) <= n:
        return data_list

    aggregated_data = []
    interval = len(data_list) // n

    for i in range(0, len(data_list), interval):
        chunk = data_list[i:i + interval]
        max_data = max(v for v in chunk)
        aggregated_data.append(max_data)

    return aggregated_data


def aggregate_time(time_list, n=500):
    """Aggregate a list of datetime objects into n data objects based on the specified time duration to reduce computation."""
    if len(time_list) <= n:
        return time_list

    aggregated_time = []
    interval = len(time_list) // n

    for i in range(0, len(time_list), interval):
        chunk = time_list[i:i + interval]
        if chunk:
            aggregated_time.append(chunk[0])  # Take the first timestamp of the chunk

    return aggregated_time


###### Logging helpers ######
def log_data(data):
    with open('data_log.csv', mode='a', newline='') as data_log:
        writer = csv.writer(data_log)
        writer.writerow(data)

def load_data():
    dts,temps,humiditys,dew_points,co2s,voc_raws,voc_indexs,nox_raws,nox_indexs,pm100s,pm25s,pm10s = [], [], [], [], [], [], [], [], [], [], [], []
    with open('data_log.csv', newline='') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            dt,temp,humidity,dew_point,co2,voc_raw,voc_index,nox_raw,nox_index,pm100,pm25,pm10=row
            dts.append(format_value(dt))
            temps.append(format_value(temp, 2))
            humiditys.append(format_value(humidity, 2))
            dew_points.append(format_value(dew_point, 2))
            co2s.append(format_value(co2))
            voc_raws.append(format_value(voc_raw))
            voc_indexs.append(format_value(voc_index))
            nox_raws.append(format_value(nox_raw))
            nox_indexs.append(format_value(nox_index))
            pm100s.append(format_value(pm100))
            pm25s.append(format_value(pm25))
            pm10s.append(format_value(pm10))

    return dts,temps,humiditys,dew_points,co2s,voc_raws,voc_indexs,nox_raws,nox_indexs,pm100s,pm25s,pm10s
