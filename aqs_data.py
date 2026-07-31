from dataclasses import dataclass, field
import csv

from utils import (format_value, calculate_heat_index, 
                    calculate_dew_point, calculate_wet_bulb)
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
    dps: list = field(default_factory=list)
    wetbulbs: list = field(default_factory=list)
    heat_indexes: list = field(default_factory=list)

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
        last_dt = self.dt
        if last_dt is None:
            return
        
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

    @property
    def dt(self):
        if self.dts:
            return self.dts[-1]
        return None
    
    @property
    def temp(self):
        if self.temps:
            return self.temps[-1]
        return None
    
    @property
    def rh(self):
        if self.humiditys:
            return self.humiditys[-1]
        return None
    
    @property
    def co2(self):
        if self.co2s:
            return self.co2s[-1]
        return None
    
    @property
    def voc_index(self):
        if self.voc_indexs:
            return self.voc_indexs[-1]
        return None
    
    @property
    def nox_index(self):
        if self.nox_indexs:
            return self.nox_indexs[-1]
        return None
    
    @property
    def pm100(self):
        if self.pm100s:
            return self.pm100s[-1]
        return None
    
    @property
    def pm25(self):
        if self.pm25s:
            return self.pm25s[-1]
        return None
    
    @property
    def pm10(self):
        if self.pm10s:
            return self.pm10s[-1]
        return None
        
    @property
    def dp(self):
        if self.temps and self.humiditys:
            return format_value(calculate_dew_point(self.temp, self.rh), 2)
        return None
    @property
    def wetbulb(self):
        if self.temps and self.humiditys:
            return format_value(calculate_wet_bulb(self.temp, self.rh), 2)
        return None

    @property
    def heat_index(self):
        if self.temps and self.humiditys:
            return format_value(calculate_heat_index(self.temp, self.rh), 2)
        return None
    