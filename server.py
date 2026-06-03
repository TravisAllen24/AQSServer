import csv

from nicegui import ui
from utils import get_y_label, aggregate_data_max, aggregate_data_avg, aggregate_time, load_data, format_value, get_relevant_data

dts, temps, humiditys, dew_points, co2s, voc_raws, voc_indexs, nox_raws, nox_indexs, pm100s, pm25s, pm10s = load_data()

def sync_missing_data():
    """Append any rows from the CSV newer than the last cached entry."""
    if not dts:
        return
    last_dt = dts[-1]
    with open('data_log.csv', newline='') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            dt = row[0]
            if dt > last_dt:
                dts.append(dt)
                temps.append(format_value(row[1], 2))
                humiditys.append(format_value(row[2], 2))
                dew_points.append(format_value(row[3], 2))
                co2s.append(format_value(row[4]))
                voc_raws.append(format_value(row[5]))
                voc_indexs.append(format_value(row[6]))
                nox_raws.append(format_value(row[7]))
                nox_indexs.append(format_value(row[8]))
                pm100s.append(format_value(row[9]))
                pm25s.append(format_value(row[10]))
                pm10s.append(format_value(row[11]))


@ui.refreshable
def plotter(timespan="Hour", data_type="T"):
    """Plot time series data based on the specified time duration and data type."""

    if data_type == 'PM':

        t1, y1 = get_relevant_data(pm10s, timespan, dts)
        _, y2 = get_relevant_data(pm25s, timespan, dts)
        _, y3 = get_relevant_data(pm100s, timespan, dts)

        agg_t1 = aggregate_time(t1, n=120)
        agg_y1 = aggregate_data_max(y1)
        agg_y2 = aggregate_data_max(y2)
        agg_y3 = aggregate_data_max(y3)

        data = [
                {
                        'type': 'scatter',
                        'name': 'Trace 3',
                        'x': agg_t1,
                        'y': agg_y3,
                        "fill": "tozeroy",
                        "mode": "none",
                        "fillcolor": '#1f77b4',
                        "name": "PM 10"
                    },
                    {
                        'type': 'scatter',
                        'name': 'Trace 2',
                        'x': agg_t1,
                        'y': agg_y2,
                        "fill": "tozeroy",
                        "mode": "none",
                        "fillcolor": '#ff7f0e',
                        "name": "PM 2.5"
                    },
                    {
                        'type': 'scatter',
                        'name': 'Trace 1',
                        'x': agg_t1,
                        'y': agg_y1,
                        "fill": "tozeroy",
                        "mode": "none",
                        "fillcolor": '#2ca02c',
                        "name": "PM 1.0"
                    },]

    else:

        ys = {
            'T': temps,
            'RH': humiditys,
            'DP': dew_points,
            'CO2': co2s,
            'VOC': voc_indexs,
            'NOX': nox_indexs
        }.get(data_type, temps)

        t, y = get_relevant_data(ys, timespan, dts)
        agg_t = aggregate_time(t)
        agg_y = aggregate_data_avg(y)


        data = [
                    {
                        'type': 'scatter',
                        'name': 'Trace 1',
                        'x': agg_t,
                        'y': agg_y,
                    },
                ]

    fig = {
            'data': data,
            'layout': {
                'title': {
                    'text': get_y_label(data_type)
                },
                'xaxis': {
                    'title': {"text":'Time'}
                },
                'yaxis': {
                    'title': {"text": get_y_label(data_type)}
                },
                # 'margin': {'l': 15, 'r': 0, 't': 0, 'b': 15},
                'plot_bgcolor': "#FFFFFF",
            },
        }

    ui.plotly(fig)


@ui.page('/')
def index_page():
    """Define the main page of the web application."""
    sync_missing_data()

    with ui.row().classes('w-full justify-center'):
        ui.label('AQS Dashboard').style('font-size: 300%; font-weight: 400')

    with ui.row().classes('w-full justify-center'):
        with ui.column():
            with ui.row().classes('w-full justify-center'):
                ui.label('Most Recent Data').style('font-size: 125%; font-weight: 500')
            with ui.card_actions():
                with ui.card():
                    with ui.grid(columns=2):
                        ui.label('Datetime:').style('font-size: 125%; font-weight: 500')
                        time_label = ui.label('-').style('font-size: 125%')

                        ui.label('Temperature: ').style('font-size: 125%; font-weight: 500')
                        temp_label = ui.label('-').style('font-size: 125%')

                        ui.label('Relative Humidity: ').style('font-size: 125%; font-weight: 500')
                        rh_label = ui.label('-').style('font-size: 125%')

                        ui.label('Dew Point: ').style('font-size: 125%; font-weight: 500')
                        dp_label = ui.label('-').style('font-size: 125%')

                        ui.label('CO2: ').style('font-size: 125%; font-weight: 500')
                        co2_label = ui.label('-').style('font-size: 125%')

                        ui.label('VOC Index: ').style('font-size: 125%; font-weight: 500')
                        voc_index_label = ui.label('-').style('font-size: 125%')

                        ui.label('NOx Index: ').style('font-size: 125%; font-weight: 500')
                        nox_index_label = ui.label('-').style('font-size: 125%')

                        ui.label('PM 10: ').style('font-size: 125%; font-weight: 500')
                        pm100_label = ui.label('-').style('font-size: 125%')

                        ui.label('PM 2.5: ').style('font-size: 125%; font-weight: 500')
                        pm25_label = ui.label('-').style('font-size: 125%')

                        ui.label('PM 1.0: ').style('font-size: 125%; font-weight: 500')
                        pm10_label = ui.label('-').style('font-size: 125%')

                    def update_labels():
                        sync_missing_data()
                        if dts:
                            time_label.set_text(dts[-1])
                            temp_label.set_text(f'{temps[-1]} C')
                            rh_label.set_text(f'{humiditys[-1]}%')
                            dp_label.set_text(f'{dew_points[-1]} C')
                            co2_label.set_text(f'{co2s[-1]} ppm')
                            voc_index_label.set_text(f'{voc_indexs[-1]} / 500')
                            nox_index_label.set_text(f'{nox_indexs[-1]} / 500')
                            pm100_label.set_text(f'{pm100s[-1]} μg/m³')
                            pm25_label.set_text(f'{pm25s[-1]} μg/m³')
                            pm10_label.set_text(f'{pm10s[-1]} μg/m³')

                    ui.timer(30, update_labels)


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
                                            value='Hour', on_change=lambda: plotter.refresh(timespan = toggle_1.value, data_type = toggle_2.value))
                        with ui.column():
                            with ui.row().classes('w-full justify-center'):
                                ui.label('Data type').style('font-size: 100%; font-weight: 500')
                            toggle_2 = ui.toggle(['T', 'RH', "DP", "CO2", "VOC", "NOX", "PM"],
                                           value='T', on_change=lambda: plotter.refresh(timespan = toggle_1.value, data_type = toggle_2.value))


def main():
    ui.run(title="AQS Webserver", favicon = '☁️', reload=False, host="0.0.0.0", port=8080)


if __name__ in {"__main__", "__mp_main__"}:
    main()
