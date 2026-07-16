import csv

from utils import format_value

class AQSData:
    def __init__(self):
        self.time = None
        self.temp = None
        self.humidity = None
        self.dew_point = None
        self.co2 = None
        self.voc_raw = None
        self.voc_index = None
        self.nox_raw = None
        self.nox_index = None
        self.pm100 = None
        self.pm25 = None
        self.pm10 = None

        self._file_pos = 0


    def update_data(self):
        with open('data_log.csv', newline='') as f:
            f.seek(self._file_pos)
            reader = csv.reader(f)
            for row in reader:
                self.time,self.temp,self.humidity,self.dew_point,self.co2,self.voc_raw,self.voc_index,self.nox_raw,self.nox_index,self.pm100,self.pm25,self.pm10=row

            self._file_pos = f.tell()


    def get_data(self, data_type, precision=0):
        """Get the latest data for the specified data type."""
        datas = vars(self)
        return format_value(datas[data_type], precision=precision)
