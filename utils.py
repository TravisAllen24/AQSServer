import datetime
import csv

### Formatting helpers ###
def format_value(value: str|int|float|None, precision: int=0) -> str:
    """Format the value or return '-' if None."""
    if value is None:
        return "-"

    if isinstance(value, str):
        try:
            return f"{round(float(value), precision):.{precision}f}"
        except ValueError:
            return value

    if isinstance(value, float):
        return f"{round(value, precision):.{precision}f}"

    return str(value)


def clean_data(data):
    data = data.replace('\n', '').replace('\r', '').split('>')[-1].split(',')

    if len(data) != 12:
        data = ['0']*12

    return data

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
def get_plot_data(time_duration, data_type):
    """Create time series data for plotting based on the specified time duration and data type."""
    t=[]
    y=[]
    now = datetime.datetime.now()

    start_time = now-delta_time(time_duration)

    with open('data_log.csv', newline='') as data_log:
        reader = csv.reader(data_log, delimiter=',')
        next(reader)
        for row in reader:
            dt,temp,humidity,dp,co2,_,voc_index,_,nox_index,pm100,pm25,pm10=row
            datas = {"T": temp,
                     "RH": humidity,
                     "DP": dp,
                     "CO2": co2,
                     "VOC": voc_index,
                     "NOX": nox_index,
                     "PM100":pm100,
                     "PM25":pm25,
                     "PM10":pm10
                     }

            data = datas[data_type]
            if dt == '0':
                continue
            if data == 'None':
                continue
            if data == '-':
                continue
            formatted_time = convert_time(dt)
            if formatted_time >= start_time:
                t.append(formatted_time)
                y.append(float(data))

    return t, y


def get_y_label(data_type):
    """Return the appropriate y-axis label based on the data type."""
    y_labels = {"T": 'Temperature (C)',
                "RH": "Relative Humidity (%)",
                "DP": "Dew Point (C)",
                "CO2": "CO2 (ppm)",
                "VOC": "VOC Index",
                "NOX": "NOX Index",
                "PM": "PM (μg/m^3)"
    }

    return y_labels.get(data_type, y_labels["T"])


def aggregate_data(data_list, n=120):
    """Aggregate a list of data into n data points based on the specified time duration to reduce computation."""
    if len(data_list) <= n:
        return data_list

    aggregated_data = []
    interval = len(data_list) // n

    for i in range(0, len(data_list), interval):
        chunk = data_list[i:i + interval]
        max_data = max(chunk)
        aggregated_data.append(max_data)

    return aggregated_data


def aggregate_time(time_list, n=120):
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
