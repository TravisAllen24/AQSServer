import os
import socket
import time

import serial  # type: ignore

from utils import clean_data, log_data, validate_data
from event_logger import get_logger


class SerialCollector:
    """Reads lines from a local USB serial port."""

    def __init__(self, com_port, baudrate, timeout):
        self.com_port = com_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.logger = get_logger("SerialCollector", "serial_collector.log")
        self._ser = None
        self.connected = False

    def connect(self):
        warned = 0
        while True:
            try:
                self._ser = serial.Serial(self.com_port, self.baudrate, timeout=self.timeout)
                self.logger.info(f"Connected to serial port {self.com_port}")
                self.connected = True
                return True
            except serial.SerialException:
                if warned >= 5:
                    self.logger.exception(f"Failed to open serial port {self.com_port}, retrying")
                    self.connected = False
                    return False
                warned += 1
                time.sleep(1)

    def read_line(self):
        """Returns raw bytes for one line, or raises to trigger reconnect."""
        if self._ser:
            raw = self._ser.readline()
            if not raw:
                self.logger.error("No data (timeout or port lost)")
            return raw
        raise serial.SerialException("Not connected to sensor")

    def close(self):
        if self._ser:
            self._ser.close()
            self.connected = False


class TCPCollector:
    """Connects out to a TCP data source (e.g. an ESP32 acting as a server)
    as a client and reads lines."""

    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.logger = get_logger("TCPCollector", "tcp_collector.log")
        self._sock = None
        self._file = None
        self.connected = False

    def connect(self):
        warned = 0
        while True:
            try:
                self._sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
                self._sock.settimeout(self.timeout)
                self._file = self._sock.makefile("rb")
                self.logger.info(f"Connected to sensor at {self.host}:{self.port}")
                self.connected = True
                return True
            except OSError:
                if warned >= 5:
                    self.logger.exception(f"Failed to connect to {self.host}:{self.port}, retrying")
                    self.connected = False
                    return False
                warned += 1
                time.sleep(1)

    def read_line(self):
        if self._file:
            raw = self._file.readline()
            if not raw:
                raise ConnectionError("Sensor disconnected")
            return raw
        raise ConnectionError("Not connected to sensor")

    def close(self):
        if self._sock:
            self._sock.close()
            self.connected = False


class DataCollector:
    """Collects data from either a local USB serial port or a TCP source."""

    def __init__(self, com_port, baudrate,
                 tcp_host, tcp_port, timeout):
        self.logger = get_logger("DataCollector", "data_collector.log")

        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.com_port = com_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.mode = None

        self.connect()


    def serial_connect(self):
        self.source = SerialCollector(com_port=self.com_port, baudrate=self.baudrate, timeout=self.timeout)
        self.mode = "serial"
        self.logger.info(f"Switched to serial port {self.com_port} for data collection")
        self.source.connect()


    def tcp_connect(self):
        self.source = TCPCollector(host=self.tcp_host, port=self.tcp_port, timeout=self.timeout)
        self.mode = "tcp"
        self.logger.info(f"Switched to TCP {self.tcp_host}:{self.tcp_port} for data collection")
        self.source.connect()


    def connect(self):
        if os.path.exists(self.com_port):
            self.serial_connect()
        else:
            self.tcp_connect()


    def run(self):
        self.logger.info(f"Data collection starting ({self.mode})")

        while True:
            if not self.source.connected:
                self.connect()
            try:
                while True:
                    if os.path.exists(self.com_port):
                        self.serial_connect()
                    try:
                        raw = self.source.read_line()
                    except Exception:
                        self.logger.exception(f"Error reading from source ({self.mode})")
                        break

                    try:
                        decoded_data = raw.decode('ascii', errors='replace')
                        cleaned_data = clean_data(decoded_data)
                        self.logger.debug(f"Data received ({self.mode}): {cleaned_data}")

                        validated_data = validate_data(cleaned_data)
                        if not validated_data:
                            continue

                        log_data(validated_data)
                        self.logger.debug(f"Data logged ({self.mode}): {validated_data}")


                    except Exception:
                        self.logger.exception(f"Error processing data from source ({self.mode})")
                        log_data(['-'] * 12)

                    time.sleep(.1)
            finally:
                self.source.close()

            time.sleep(1)  # brief pause before reconnect loop restarts


if __name__ == "__main__":
    # USB serial mode:
    data_collector = DataCollector(
        com_port="/dev/aqs-sensor", baudrate=115200,
        tcp_host="192.168.1.46", tcp_port=65432,
        timeout=60
    )

    data_collector.run()