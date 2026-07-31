from nicegui import ui, app
from event_logger import get_logger
from aqs_data import AQSData
from utils import get_y_label, aggregate_data_max, aggregate_data_avg, aggregate_time, get_relevant_data

logger = get_logger("AQSWebServer", "webserver.log")

def log_error(exception: Exception):
    logger.error(f"Framework Exception Caught: {exception}", exc_info=True)

app.on_exception(log_error)

aqs = AQSData()

@ui.refreshable
def plotter(timespan="Hour", data_type="T", is_dark=False):
    """Plot time series data based on the specified time duration and data type."""

    
    paper_color = "#222222" if is_dark else None
    bg_color =  "#222222" if is_dark else "#FFFFFF"
    grid_color = "#303030" if is_dark else '#EEEEEE'
    text_color = "#FFFFFF" if is_dark else None
    line_color = '#686ffc' if is_dark else '#1f77b4'
    pm100_color = "#4ba3e3" if is_dark else '#1f77b4'
    pm25_color  = "#ff9f43" if is_dark else '#ff7f0e'
    pm10_color  = "#51cf66" if is_dark else '#2ca02c'


    if data_type == 'PM':

        t1, y1 = get_relevant_data(aqs.pm10s, timespan, aqs.dts)
        _, y2 = get_relevant_data(aqs.pm25s, timespan, aqs.dts)
        _, y3 = get_relevant_data(aqs.pm100s, timespan, aqs.dts)

        agg_t1 = aggregate_time(t1, n=120)
        agg_y1 = aggregate_data_max(y1)
        agg_y2 = aggregate_data_max(y2)
        agg_y3 = aggregate_data_max(y3)

        data = [
                {
                        'type': 'scatter',
                        'x': agg_t1,
                        'y': agg_y3,
                        "fill": "tozeroy",
                        "mode": "none",
                        "fillcolor": pm100_color,
                        "name": "PM 10"
                    },
                    {
                        'type': 'scatter',
                        'x': agg_t1,
                        'y': agg_y2,
                        "fill": "tozeroy",
                        "mode": "none",
                        "fillcolor": pm25_color,
                        "name": "PM 2.5"
                    },
                    {
                        'type': 'scatter',
                        'x': agg_t1,
                        'y': agg_y1,
                        "fill": "tozeroy",
                        "mode": "none",
                        "fillcolor": pm10_color,
                        "name": "PM 1.0"
                    },]

    else:

        ys = {
            'T': aqs.temps,
            'RH': aqs.humiditys,
            'DP': aqs.dew_points,
            'CO2': aqs.co2s,
            'VOC': aqs.voc_indexs,
            'NOX': aqs.nox_indexs
        }.get(data_type, aqs.temps)

        t, y = get_relevant_data(ys, timespan, aqs.dts)
        agg_t = aggregate_time(t)
        agg_y = aggregate_data_avg(y)


        data = [
                    {
                        'type': 'scatter',
                        'name': 'Trace 1',
                        'x': agg_t,
                        'y': agg_y,
                        'line': {
                        'color': line_color},
                    },
                ]

    fig_config = {
            'data': data,
            'layout': {
                'title': {
                    'text': get_y_label(data_type) + f' over Time ({"Max" if timespan == "Max" else f"1 {timespan}"})',
                    'font': {'color': text_color}
                },
                'xaxis': {
                    'title': {"text":'Time',
                              'font': {'color': text_color}},
                    'gridcolor': grid_color,
                    'tickfont': {'color': text_color},
                    'zerolinecolor': grid_color,
                },
                'yaxis': {
                    'title': {"text": get_y_label(data_type),
                              'font': {'color': text_color}},
                    'gridcolor': grid_color,
                    'tickfont': {'color': text_color},
                    'zerolinecolor': grid_color,
                },
                'plot_bgcolor': bg_color,
                'paper_bgcolor': paper_color,
            },
        }

    ui.plotly(fig_config).classes('w-full h-full')

@ui.page('/')
def index_page():
    """Define the main page of the web application."""
    aqs.sync()

    FIELDS = [
        ('Datetime:',        lambda: aqs.dts[-1],          '{}'),
        ('Temperature: ',    lambda: aqs.temps[-1],        '{} C'),
        ('Relative Humidity: ', lambda: aqs.humiditys[-1], '{}%'),
        ('Dew Point: ',      lambda: aqs.dew_points[-1],   '{} C'),
        ('CO2: ',            lambda: aqs.co2s[-1],         '{} ppm'),
        ('VOC Index: ',      lambda: aqs.voc_indexs[-1],   '{} / 500'),
        ('NOx Index: ',      lambda: aqs.nox_indexs[-1],   '{} / 500'),
        ('PM 10: ',          lambda: aqs.pm100s[-1],       '{} μg/m³'),
        ('PM 2.5: ',         lambda: aqs.pm25s[-1],        '{} μg/m³'),
        ('PM 1.0: ',         lambda: aqs.pm10s[-1],        '{} μg/m³'),
    ]

    STYLE_SECTION_HEADER = 'font-size: 125%; font-weight: 500'
    STYLE_VALUE = 'font-size: 125%'
    STYLE_SUBHEADER = 'font-size: 100%; font-weight: 500'
    STYLE_TITLE = 'font-size: 300%; font-weight: 400'
    STYLE_MUTED = 'color: grey'
    STYLE_FOOTER = 'background-color: transparent; border-top: none;'

    CLASS_CENTERED_ROW = 'w-full justify-center'
    CLASS_TREND_CARD = 'w-full md:w-[700px] mx-auto overflow-hidden p-2'
    CLASS_REFRESH_BTN = 'absolute right-2 bottom-2'
    CLASS_FOOTER = 'w-full justify-end items-end'

    def refresh_plot():
        plotter.refresh(timespan=toggle_1.value, 
                        data_type=toggle_2.value, 
                        is_dark=dark_mode_switch.value)

    def update_labels():
        aqs.sync()
        if aqs.dts:
            for lbl, (_, getter, fmt) in zip(value_labels, FIELDS):
                lbl.set_text(fmt.format(getter()))

    with ui.row().classes(CLASS_CENTERED_ROW):
        ui.label('AQS Dashboard').style(STYLE_TITLE)

    with ui.row().classes(CLASS_CENTERED_ROW):
        with ui.column():
            with ui.row().classes(CLASS_CENTERED_ROW):
                ui.label('Most Recent Data').style(STYLE_SECTION_HEADER)
            with ui.card_actions():
                with ui.card():
                    with ui.grid(columns=2):
                        value_labels = []
                        for name, _, _ in FIELDS:
                            ui.label(name).style(STYLE_SECTION_HEADER)
                            value_labels.append(ui.label('-').style(STYLE_VALUE))

                    ui.timer(30, update_labels)

        with ui.column():
            with ui.row().classes(CLASS_CENTERED_ROW):
                ui.label('Data Time Trend').style(STYLE_SECTION_HEADER)
            with ui.card_actions():
                with ui.card().classes(CLASS_TREND_CARD):
                    plotter()
                    with ui.row().classes(CLASS_CENTERED_ROW):
                        with ui.column():
                            with ui.row().classes(CLASS_CENTERED_ROW):
                                ui.label('Time period').style(STYLE_SUBHEADER)
                            toggle_1 = ui.toggle(['Hour', 'Day', "Week", "Month", "Max"],
                                            value='Hour', on_change=refresh_plot)
                        with ui.column():
                            with ui.row().classes(CLASS_CENTERED_ROW):
                                ui.label('Data type').style(STYLE_SUBHEADER)
                            toggle_2 = ui.toggle(['T', 'RH', "DP", "CO2", "VOC", "NOX", "PM"],
                                           value='T', on_change=refresh_plot)
                        with ui.column():
                            ui.button(icon='refresh', on_click=refresh_plot
                                      ).classes(CLASS_REFRESH_BTN).style(STYLE_MUTED).tooltip('Refresh Plot')

    with ui.footer().classes(CLASS_FOOTER).style(STYLE_FOOTER):
            dark = ui.dark_mode()
            dark_mode_switch = ui.switch('Dark mode', on_change=refresh_plot).bind_value(dark).style(STYLE_MUTED)


def main():
    logger.info("Starting AQS Webserver...")
    ui.run(title="AQS Webserver", favicon = "media/wind.ico", host="0.0.0.0", port=8080, reload=False)


if __name__ in {"__main__", "__mp_main__"}:
    main()
