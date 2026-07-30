import socket
import time

import serial  # type: ignore

from utils import clean_data, log_data, validate_data
from event_logger import get_logger


class SerialLineSource:
    """Reads lines from a local USB serial port. Reconnects on failure."""

    def __init__(self, com_port="/dev/aqs-sensor", baudrate=115200):
        self.com_port = com_port
        self.baudrate = baudrate
        self.logger = get_logger("SerialLineSource", "serial_source.log")
        self._ser = None

    def connect(self):
        while True:
            try:
                self._ser = serial.Serial(self.com_port, self.baudrate, timeout=1)
                self.logger.info(f"Connected to serial port {self.com_port}")
                return
            except serial.SerialException:
                self.logger.exception(f"Failed to open serial port {self.com_port}, retrying")
                time.sleep(1)

    def read_line(self):
        """Returns raw bytes for one line, or raises to trigger reconnect."""
        raw = self._ser.readline()
        if not raw:
            raise serial.SerialException("No data (timeout or port lost)")
        return raw

    def close(self):
        if self._ser:
            self._ser.close()


class TCPLineSource:
    """Connects out to a TCP data source (e.g. an ESP32 acting as a server)
    as a client and reads lines. Reconnects on failure."""

    def __init__(self, host="192.168.1.194", port=65432):
        self.host = host
        self.port = port
        self.logger = get_logger("TCPLineSource", "tcp_source.log")
        self._sock = None
        self._file = None

    def connect(self):
        while True:
            try:
                self._sock = socket.create_connection((self.host, self.port), timeout=5)
                self._sock.settimeout(5)
                self._file = self._sock.makefile("rb")
                self.logger.info(f"Connected to sensor at {self.host}:{self.port}")
                return
            except OSError:
                self.logger.exception(f"Failed to connect to {self.host}:{self.port}, retrying")
                time.sleep(1)

    def read_line(self):
        raw = self._file.readline()
        if not raw:
            raise ConnectionError("Sensor disconnected")
        return raw

    def close(self):
        if self._sock:
            self._sock.close()


class LogServerClient:
    """Connects out to a remote log/dashboard server as a client and pushes
    data to it. This replaces the old broadcast server: instead of listeners
    connecting in, we connect out to a single known server.

    Sending is best-effort and non-blocking: a dropped connection is logged
    and retried on a timer, but never stalls data collection.
    """

    RECONNECT_INTERVAL = 5  # seconds between reconnect attempts

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.logger = get_logger("LogServerClient", "log_server_client.log")
        self._sock = None
        self._connected = False
        self._last_attempt = 0.0

    def connect(self):
        """Blocking connect with retry. Used for the initial connection."""
        while not self._try_connect():
            time.sleep(self.RECONNECT_INTERVAL)

    def maybe_reconnect(self):
        """Non-blocking: attempts a reconnect at most once per RECONNECT_INTERVAL.
        Safe to call on every loop iteration."""
        if self._connected:
            return
        now = time.time()
        if now - self._last_attempt < self.RECONNECT_INTERVAL:
            return
        self._last_attempt = now
        self._try_connect()

    def send(self, data):
        """Best-effort send; drops the connection on failure so the next
        maybe_reconnect() call re-establishes it. Never raises."""
        if not self._connected:
            return
        try:
            self._sock.sendall(data)
        except (TimeoutError, ConnectionResetError, BrokenPipeError, OSError):
            self.logger.exception("Error sending to log server, will reconnect")
            self._connected = False
            self.close()

    def _try_connect(self):
        try:
            self._sock = socket.create_connection((self.host, self.port), timeout=5)
            self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.logger.info(f"Connected to log server at {self.host}:{self.port}")
            self._connected = True
            return True
        except OSError:
            self.logger.exception(f"Failed to connect to log server {self.host}:{self.port}, retrying")
            self._connected = False
            return False

    def close(self):
        if self._sock:
            self._sock.close()
        self._connected = False


class DataCollector:
    """Reads lines from a local sensor source (serial or TCP) and forwards
    each line to a remote log server over TCP, while also logging locally."""

    def __init__(self, mode="serial", com_port="/dev/aqs-sensor", baudrate=115200,
                 esp32_host=None, esp32_port=None,
                 log_server_host="192.168.1.100", log_server_port=65432):
        assert mode in ("serial", "tcp"), "mode must be 'serial' or 'tcp'"
        self.mode = mode
        self.logger = get_logger("DataCollector", "data_collector.log")

        if mode == "serial":
            self.source = SerialLineSource(com_port=com_port, baudrate=baudrate)
        else:
            assert esp32_host and esp32_port, "esp32_host/esp32_port required for tcp mode"
            self.source = TCPLineSource(esp32_host, esp32_port)

        self.log_client = LogServerClient(log_server_host, log_server_port)

    def run(self):
        self.logger.info(f"Data collection starting in '{self.mode}' mode")
        self.log_client.connect()

        while True:
            self.source.connect()
            try:
                while True:
                    self.log_client.maybe_reconnect()

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
                        self.log_client.send(raw)

                    except Exception:
                        self.logger.exception(f"Error processing data from source ({self.mode})")
                        log_data(['-'] * 12)
            finally:
                self.source.close()

            time.sleep(1)  # brief pause before reconnect loop restarts


if __name__ == "__main__":
    # USB serial mode:
    data_collector = DataCollector(
        mode="serial", com_port="/dev/aqs-sensor",
        log_server_host="192.168.1.194", log_server_port=65432,
    )

    # TCP mode (ESP32 as server, this collector connects out to it as a client):
    # data_collector = DataCollector(
    #     mode="tcp", esp32_host="192.168.1.50", esp32_port=65432,
    #     log_server_host="192.168.1.100", log_server_port=65432,
    # )

    data_collector.run()