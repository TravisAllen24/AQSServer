import csv

from utils import format_value

class AQSData:
    def __init__(self):
        self.dt = []
        self.temp = []
        self.humidity = []
        self.dew_point = []
        self.co2 = []
        self.voc_raw = []
        self.voc_index = []
        self.nox_raw = []
        self.nox_index = []
        self.pm100 = []
        self.pm25 = []
        self.pm10 = []

        self.load_data()

    def validate_data(self, data):
        if not data or len(data) != 12:
            return False
        return True

    def load_data(self):
        """Load data from the CSV file into memory."""
        with open('data_log.csv', newline='') as data_log:
            reader = csv.reader(data_log, delimiter=',')
            next(reader)
            for row in reader:
                if self.validate_data(row):
                    dt,temp,humidity,dp,co2,voc_raw,voc_index,nox_raw,nox_index,pm100,pm25,pm10=row
                    self.dt.append(dt)
                    self.temp.append(temp)
                    self.humidity.append(humidity)
                    self.dew_point.append(dp)
                    self.co2.append(co2)
                    self.voc_raw.append(voc_raw)
                    self.voc_index.append(voc_index)
                    self.nox_raw.append(nox_raw)
                    self.nox_index.append(nox_index)
                    self.pm100.append(pm100)
                    self.pm25.append(pm25)
                    self.pm10.append(pm10)


    def update_data(self):
        """Add latest line from the CSV file to memory."""
        with open('data_log.csv', newline='') as data_log:
            reader = csv.reader(data_log, delimiter=',')
            next(reader)
            for row in reader:
                if self.validate_data(row):
                    dt,temp,humidity,dp,co2,voc_raw,voc_index,nox_raw,nox_index,pm100,pm25,pm10=row
                    if dt in self.dt:
                        continue
                    self.dt.append(dt)
                    self.temp.append(temp)
                    self.humidity.append(humidity)
                    self.dew_point.append(dp)
                    self.co2.append(co2)
                    self.voc_raw.append(voc_raw)
                    self.voc_index.append(voc_index)
                    self.nox_raw.append(nox_raw)
                    self.nox_index.append(int(nox_index))
                    self.pm100.append(int(pm100))
                    self.pm25.append(int(pm25))
                    self.pm10.append(int(pm10))


    def get_data(self, data_type):
        """Get the latest data for the specified data type."""
        return {   "time": self.dt,
                    "T": self.temp,
                    "RH": self.humidity,
                    "DP": self.dew_point,
                    "CO2": self.co2,
                    "VOC": self.voc_raw,
                    "VOC_Index": self.voc_index,
                    "NOX_Raw": self.nox_raw,
                    "NOX_Index": self.nox_index,
                    "PM10": self.pm10,
                    "PM25": self.pm25,
                    "PM100": self.pm100
                }.get(data_type, self.temp)


    def get_latest_data(self, data_type, precision=0):
        """Get the latest data for the specified data type."""

        data = self.get_data(data_type)
        if data:
            return format_value(data[-1], precision=precision)

        return "-"

