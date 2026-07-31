from dataclasses import dataclass, field
import csv

from utils import format_value

@dataclass
class AQSData:
    dts: list = field(default_factory=list)
    temps: list = field(default_factory=list)
    humiditys: list = field(default_factory=list)
    co2s: list = field(default_factory=list)
    voc_raws: list = field(default_factory=list)
    voc_indexs: list = field(default_factory=list)
    nox_raws: list = field(default_factory=list)
    nox_indexs: list = field(default_factory=list)
    pm100s: list = field(default_factory=list)
    pm25s: list = field(default_factory=list)
    pm10s: list = field(default_factory=list)


    def __post_init__(self):
        self.load_data()


    def load_data(self):
        with open('data_log.csv', newline='') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                dt,temp,humidity,co2,voc_raw,voc_index,nox_raw,nox_index,pm100,pm25,pm10=row
                self.dts.append(format_value(dt))
                self.temps.append(format_value(temp, 2))
                self.humiditys.append(format_value(humidity, 2))
                self.co2s.append(format_value(co2))
                self.voc_raws.append(format_value(voc_raw))
                self.voc_indexs.append(format_value(voc_index))
                self.nox_raws.append(format_value(nox_raw))
                self.nox_indexs.append(format_value(nox_index))
                self.pm100s.append(format_value(pm100))
                self.pm25s.append(format_value(pm25))
                self.pm10s.append(format_value(pm10))


    def sync(self):
        """Append any rows from the CSV newer than the last cached entry."""
        if not self.dts:
            return
        last_dt = self.dts[-1]
        with open('data_log.csv', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                dt = row[0]
                if dt > last_dt:
                    self.dts.append(dt)
                    self.temps.append(format_value(row[1], 2))
                    self.humiditys.append(format_value(row[2], 2))
                    self.co2s.append(format_value(row[4]))
                    self.voc_raws.append(format_value(row[5]))
                    self.voc_indexs.append(format_value(row[6]))
                    self.nox_raws.append(format_value(row[7]))
                    self.nox_indexs.append(format_value(row[8]))
                    self.pm100s.append(format_value(row[9]))
                    self.pm25s.append(format_value(row[10]))
                    self.pm10s.append(format_value(row[11]))