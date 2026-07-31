import datetime
import csv
import math
import threading
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
    return data.replace('\n', '').replace('\r', '')


def validate_data(data):
    data = data.split(',')

    if len(data) != 12 or data[0] != "$AQS":
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
def get_y_label(data_type, temp_unit="C"):
    """Return the appropriate y-axis label based on the data type."""
    y_labels = {"T": f'Temperature ({temp_unit})',
                "RH": "Relative Humidity (%)",
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
_log_lock = threading.Lock()

def log_data(data):
    with _log_lock:
        with open('data_log.csv', mode='a', newline='') as data_log:
            writer = csv.writer(data_log)
            writer.writerow(data)


###### Temperature and Humidity Calculations ######
def calculate_heat_index(t, rh):
    """Calculate the heat index given temperature (T) in Fahrenheit 
    and relative humidity (RH) in percent."""
    if t is None or rh is None:
        return None

    hi = 0.5 * (t + 61.0 + ((t-68.0)*1.2) + (rh*0.094))

    if hi > 80:
            hi = (-42.379 + 2.04901523*t + 10.14333127*rh - .22475541*t*rh 
            - .00683783*t*t - .05481717*rh*rh + .00122874*t*t*rh 
            + .00085282*t*rh*rh - .00000199*t*t*rh*rh)

    if rh < 13 and 80 <= t <= 112:
         hi -= ((13 - rh) / 4) * math.sqrt((17 - abs(t - 95.)) / 17)

    elif rh > 85 and 80 <= t <= 87:
        hi += ((rh-85)/10) * ((87-t)/5)

    return hi


# Dew point calculation function
def calculate_dew_point(temp_c: float|None, rh: float|None) -> float|None:
    """
    Calculate the dew point temperature (°C) given temperature (°C) and relative humidity (%).
    Uses the Magnus formula, suitable for typical indoor conditions.
    Returns None if inputs are invalid.
    """
    if temp_c is None or rh is None:
        return None
    # Magnus formula constants for water vapor over water
    a = 17.62
    b = 243.12  # °C
    try:
        alpha = ((a * temp_c) / (b + temp_c)) + (math.log(rh / 100.0))
        dew_point = (b * alpha) / (a - alpha)
        return round(dew_point, 2)
    except Exception:
        return None


def calculate_wet_bulb(temp_c: float|None, rh: float|None) -> float|None:
    """Stull (2011) empirical approximation, accurate to ~1°C for -20 to 50°C, 5-99% RH."""
    if temp_c is None or rh is None:
        return None
    return (temp_c * math.atan(0.151977 * (rh + 8.313659) ** 0.5)
            + math.atan(temp_c + rh)
            - math.atan(rh - 1.676331)
            + 0.00391838 * rh ** 1.5 * math.atan(0.023101 * rh)
            - 4.686035)

def c_to_f(celsius: float|None) -> float|None:
    """Convert Celsius to Fahrenheit."""
    if celsius is None:
        return None
    return (celsius * 9/5) + 32


def ensure_units(temp, unit):
    """Ensure the temperature is in the specified unit ('C' or 'F')."""
    if temp is None:
        return None
    if unit == 'F':
        return c_to_f(temp)
    return temp
