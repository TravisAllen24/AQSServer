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

    if len(data) != 10:
        data = ['0']*10

    return data

###### Time helpers ######
def convert_time(time):
    """Convert a string time to a datetime object."""
    return datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')


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
def create_timeseries(time_duration, data_type):
    """Create time series data for plotting based on the specified time duration and data type."""
    t=[]
    y=[]
    now = datetime.datetime.now()

    start_time = now-delta_time(time_duration)

    with open('data_log.csv', newline='') as data_log:
        reader = csv.reader(data_log, delimiter=',')
        next(reader)
        for row in reader:
            dt,temp,humidity,dp,co2,voc_raw,voc_index,pm10,pm25,pm100=row
            datas = {"T": temp,
                     "RH": humidity,
                     "DP": dp,
                     "CO2": co2,
                     "VOC": voc_index,
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
    }

    return y_labels.get(data_type, y_labels["T"])


###### Logging helpers ######
def log_data(data):
    with open('data_log.csv', mode='a', newline='') as data_log:
        writer = csv.writer(data_log)
        writer.writerow(data)


def get_latest_data(data_type, precision=0):
    """Retrieve the latest data for the specified data type from the CSV log."""
    last_row = "-,-,-,-,-,-,-,-,-,-"
    with open('data_log.csv', newline='') as data_log:
        reader = csv.reader(data_log, delimiter=',')
        next(reader)

        for row in reader:
            last_row = row

    dt,temp,humidity,dp,co2,voc_raw,voc_index,pm100,pm25,pm10=last_row

    datas = {   "time": dt,
                "temp": temp,
                "humidity": humidity,
                "dew_point": dp,
                "co2": co2,
                "voc_raw": voc_raw,
                "voc_index": voc_index,
                "pm10": pm10,
                "pm25": pm25,
                "pm100": pm100
            }

    return format_value(datas.get(data_type, datas["time"]), precision=precision)
