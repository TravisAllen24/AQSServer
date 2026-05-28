from nicegui import ui, app
import serial
import asyncio
import csv
import datetime

import matplotlib
matplotlib.use('Agg')

port = 'COM4'

def create_serial():
    global ser
    ser = serial.Serial(baudrate = 115200, port=port)
    ser.reset_input_buffer()


def format_value(value: int|float|None, precision: int=0) -> str:
    """Format the value or return '----' if None."""
    if value is None:
        return "----"
    if isinstance(value, float):
        return f"{round(value, precision):.{precision}f}"
    return str(value)


def parse_data(data):
    data = data.replace('\n', '').replace('\r', '').split('>')[-1].split(',')

    if len(data) != 10:
        return ['0']*10

    return data


def log_data(data):
    with open('data_log.csv', mode='a', newline='') as data_log:
        writer = csv.writer(data_log)
        writer.writerow(data)


async def read_serial():
    global latest_data
    latest_data = ['0']*10
    while True:
        try:
            raw_data = ser.readline().decode('ascii')
            latest_data = parse_data(raw_data)
            log_data(latest_data)
            ser.reset_input_buffer()

        except Exception as e:
            print(f'Error: {e}')
            latest_data = ['0']*10

        await asyncio.sleep(5)


def convert_time(time):
    return datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')


def delta_time(time_duration):
    delta = {"Hour": datetime.timedelta(hours=1),
             "Day": datetime.timedelta(days=1),
             "Week": datetime.timedelta(days=7),
             "Month": datetime.timedelta(days=30),
             "Max": datetime.timedelta(days=365)
             }

    return delta.get(time_duration, delta["Max"])


def create_timeseries(time_duration, data_type):
    t=[]
    y=[]
    now = datetime.datetime.now() - datetime.timedelta(hours=2)

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
            formatted_time = convert_time(dt)
            if formatted_time >= start_time:
                t.append(formatted_time)
                y.append(float(data))

    return t, y


def get_y_label(data_type):
    y_labels = {"T": 'Temperature (C)',
                "RH": "Relative Humidity (%)",
                "DP": "Dew Point (C)",
                "CO2": "CO2 (ppm)",
                "VOC": "VOC Index",
    }

    return y_labels.get(data_type, y_labels["T"])


def aggregate_data(ts, xs, time_duration):
    aggregation_mapping = {"Hour": 1,
             "Day": 210,
             "Week": 840,
             "Month": 3360,
             "Max": 40320
             }
    t = []
    x = []
    step = aggregation_mapping[time_duration]
    for i in range(len(ts)):
        if i % step == 0:
            t.append(ts[i])
            x.append(xs[i])

    return t, x


@ui.refreshable
def plotter(time_duration = 'Hour', data_type = "T"):

    if data_type == 'PM':
        with ui.matplotlib(figsize=(8, 4)).figure as fig:
            ax = fig.gca()
            t3, y1 = create_timeseries(time_duration, 'PM100')
            t2, y2 = create_timeseries(time_duration, 'PM25')
            t1, y3 = create_timeseries(time_duration, 'PM10')

            ax.plot(t1, y1, zorder=1, color='C2')
            ax.plot(t2, y2, zorder=2, color='C1')
            ax.plot(t3, y3, zorder=3, color='C0')
            ax.set_xlabel('Time')
            ax.set_ylabel('PM (μg/c^3)')

            ax.fill_between(t1, y1, color='C2')
            ax.fill_between(t1, y1, y2, color='C1')
            ax.fill_between(t1, y2, y3, color='C0')

            ax.legend(['PM 1.0', 'PM 2.5', 'PM 10'], loc='upper right')

    else:
        with ui.matplotlib(figsize=(8, 4)).figure as fig:
            t, y = create_timeseries(time_duration, data_type)
            ax = fig.gca()
            ax.plot(t, y, '-')
            ax.set_xlabel('Time')
            ax.set_ylabel(get_y_label(data_type))


app.on_startup(create_serial)
app.on_startup(read_serial)

@ui.page('/')
def index_page():
    with ui.row().classes('w-full justify-center'):
        ui.label('AQS Dashboard').style('font-size: 300%; font-weight: 400')

    with ui.row().classes('w-full justify-center'):
        with ui.column():
            with ui.row().classes('w-full justify-center'):
                ui.label('Most Recent Data').style('font-size: 125%; font-weight: 500')
            with ui.card_actions():
                with ui.card():
                    with ui.grid(columns=2):
                        ui.label('dt:').style('font-size: 125%; font-weight: 500')
                        time_label = ui.label().style('font-size: 125%')

                        ui.label('Temperature: ').style('font-size: 125%; font-weight: 500')
                        temp_label = ui.label().style('font-size: 125%')

                        ui.label('Relative Humidity: ').style('font-size: 125%; font-weight: 500')
                        rh_label = ui.label().style('font-size: 125%')

                        ui.label('Dew Point: ').style('font-size: 125%; font-weight: 500')
                        dp_label = ui.label().style('font-size: 125%')

                        ui.label('CO2: ').style('font-size: 125%; font-weight: 500')
                        co2_label = ui.label().style('font-size: 125%')

                        ui.label('VOC Raw: ').style('font-size: 125%; font-weight: 500')
                        voc_raw_label = ui.label().style('font-size: 125%')

                        ui.label('VOC Index: ').style('font-size: 125%; font-weight: 500')
                        voc_index_label = ui.label().style('font-size: 125%')

                        ui.label('NOx Raw: ').style('font-size: 125%; font-weight: 500')
                        nox_raw_label = ui.label('0').style('font-size: 125%')

                        ui.label('NOx Index: ').style('font-size: 125%; font-weight: 500')
                        nox_index_label = ui.label('0').style('font-size: 125%')

                        ui.label('PM 10: ').style('font-size: 125%; font-weight: 500')
                        pm100_label = ui.label().style('font-size: 125%')

                        ui.label('PM 2.5: ').style('font-size: 125%; font-weight: 500')
                        pm25_label = ui.label().style('font-size: 125%')

                        ui.label('PM 1.0: ').style('font-size: 125%; font-weight: 500')
                        pm10_label = ui.label().style('font-size: 125%')

                    ui.timer(1, lambda: (time_label.set_text(latest_data[0]),
                                        temp_label.set_text(f'{latest_data[1]} C'),
                                        rh_label.set_text(f'{format_value(float(latest_data[2]), 2)}%'),
                                        dp_label.set_text(f'{latest_data[3]} C'),
                                        co2_label.set_text(f'{latest_data[4]} ppm'),
                                        voc_raw_label.set_text(f'{latest_data[5]}'),
                                        voc_index_label.set_text(f'{latest_data[6]}'),
                                        pm100_label.set_text(f'{latest_data[7]} μg/c^3'),
                                        pm25_label.set_text(f'{latest_data[8]} μg/c^3'),
                                        pm10_label.set_text(f'{latest_data[9]} μg/c^3'),))


        with ui.column():
            with ui.row().classes('w-full justify-center'):
                ui.label('Data Time Trend').style('font-size: 125%; font-weight: 500')
            with ui.card_actions():
                with ui.card():
                    plotter()
                    with ui.row().classes('w-full justify-center'):
                        with ui.column():
                            with ui.row().classes('w-full justify-center'):
                                ui.label('Time period').style('font-size: 100%; font-weight: 500')
                            toggle_1 = ui.toggle(['Hour', 'Day', "Week", "Month", "Max"],
                                            value='Hour', on_change=lambda: plotter.refresh(time_duration = toggle_1.value, data_type = toggle_2.value))
                        with ui.column():
                            with ui.row().classes('w-full justify-center'):
                                ui.label('Data type').style('font-size: 100%; font-weight: 500')
                            toggle_2 = ui.toggle(['T', 'RH', "DP", "CO2", "VOC", "PM"],
                                           value='T', on_change=lambda: plotter.refresh(time_duration = toggle_1.value, data_type = toggle_2.value))


def main():
    ui.run(title="AQS Webserver", favicon = '☁️', reload=False, host="0.0.0.0", port=8080)

main()
