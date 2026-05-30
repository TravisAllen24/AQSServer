from nicegui import ui
from utils import get_plot_data, get_y_label, get_latest_data, aggregate_data, aggregate_time


@ui.refreshable
def plotter(time_duration = 'Hour', data_type = "T"):
    """Plot time series data based on the specified time duration and data type."""

    if data_type == 'PM':
        with ui.matplotlib(figsize=(8, 4)).figure as fig:
            ax = fig.gca()
            t1, y1 = get_plot_data(time_duration, 'PM100')
            _, y2 = get_plot_data(time_duration, 'PM25')
            _, y3 = get_plot_data(time_duration, 'PM10')

            agg_t1 = aggregate_time(t1)
            agg_y1 = aggregate_data(y1)
            agg_y2 = aggregate_data(y2)
            agg_y3 = aggregate_data(y3)

            ax.fill_between(agg_t1, agg_y3, linewidth=0, color='C2')
            ax.fill_between(agg_t1, agg_y2, agg_y3, linewidth=0, color='C1')
            ax.fill_between(agg_t1, agg_y1, agg_y2, linewidth=0, color='C0')

            ax.set_xlabel('Time')
            ax.set_ylabel(data_type)
            ax.legend(['PM 1.0', 'pm 2.5', 'pm 10'], loc='upper left')

    else:
        with ui.matplotlib(figsize=(8, 4)).figure as fig:
            t, y = get_plot_data(time_duration, data_type)
            ax = fig.gca()
            ax.plot(t, y, '-')
            ax.set_xlabel('Time')
            ax.set_ylabel(get_y_label(data_type))


@ui.page('/')
def index_page():
    """Define the main page of the web application."""
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

                    ui.timer(1, lambda: (time_label.set_text(get_latest_data('time')),
                                        temp_label.set_text(f'{get_latest_data('temp')} C'),
                                        rh_label.set_text(f'{get_latest_data('humidity', 2)}%'),
                                        dp_label.set_text(f'{get_latest_data('dew_point')} C'),
                                        co2_label.set_text(f'{get_latest_data('co2')} ppm'),
                                        voc_index_label.set_text(f'{get_latest_data('voc_index')} / 500'),
                                        pm100_label.set_text(f'{get_latest_data('pm100')} μg/c^3'),
                                        pm25_label.set_text(f'{get_latest_data('pm25')} μg/c^3'),
                                        pm10_label.set_text(f'{get_latest_data('pm10')} μg/c^3'),))


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


if __name__ in {"__main__", "__mp_main__"}:
    main()
