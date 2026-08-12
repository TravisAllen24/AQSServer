from dataclasses import dataclass, field
import csv

from utils import (format_value, calculate_heat_index,
                    calculate_dew_point, calculate_wet_bulb)
@dataclass
class AQSData:
    csv_path: str = 'data_log.csv'
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
    _file_pos: int = 0

    def __post_init__(self):
        self.load_data()

    def _append_row(self, row: list[str]) -> None:
        if len(row) != 11:
            return

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

    def load_data(self):
        with open(self.csv_path, newline='') as f:
            next(f, None)  # skip header
            for line in f:
                row = next(csv.reader([line]))
                self._append_row(row)
            self._file_pos = f.tell()

    def sync(self):
        """Append only new CSV rows since the last read using seek/tell."""
        with open(self.csv_path, newline='') as f:
            f.seek(self._file_pos)

            while True:
                row_start = f.tell()
                line = f.readline()

                if not line:
                    break

                # Avoid consuming a partially written trailing line.
                if not line.endswith('\n'):
                    f.seek(row_start)
                    break

                row = next(csv.reader([line]))
                self._append_row(row)

            self._file_pos = f.tell()

    @property
    def dt(self) -> str|None:
        if self.dts:
            return self.dts[-1]
        return None

    @property
    def temp(self) -> float|None:
        if self.temps:
            return self.temps[-1]
        return None

    @property
    def rh(self) -> float|None:
        if self.humiditys:
            return self.humiditys[-1]
        return None

    @property
    def co2(self) -> int|None:
        if self.co2s:
            return self.co2s[-1]
        return None

    @property
    def voc_index(self) -> int|None:
        if self.voc_indexs:
            return self.voc_indexs[-1]
        return None

    @property
    def nox_index(self) -> int|None:
        if self.nox_indexs:
            return self.nox_indexs[-1]
        return None

    @property
    def pm100(self) -> int|None:
        if self.pm100s:
            return self.pm100s[-1]
        return None

    @property
    def pm25(self) -> int|None:
        if self.pm25s:
            return self.pm25s[-1]
        return None

    @property
    def pm10(self) -> int|None:
        if self.pm10s:
            return self.pm10s[-1]
        return None

    @property
    def dp(self) -> float|None:
        if self.temps and self.humiditys:
            return calculate_dew_point(self.temp, self.rh)
        return None
    @property
    def wetbulb(self) -> float|None:
        if self.temps and self.humiditys:
            return calculate_wet_bulb(self.temp, self.rh)
        return None

    @property
    def heat_index(self) -> float|None:
        if self.temps and self.humiditys:
            return calculate_heat_index(self.temp, self.rh)
        return None
