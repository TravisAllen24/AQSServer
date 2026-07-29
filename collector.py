import socket
import time
import threading
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

import serial  # type: ignore

from utils import clean_data, log_data, validate_data
from event_logger import get_logger


class SerialLineSource:
    """Reads lines from a local USB serial port. Reconnects on failure."""

    def __init__(self, com_port="COM14", baudrate=115200):
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


class TCPClientLineSource:
    """Connects out to the ESP32 as a client and reads lines. Reconnects on failure."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.logger = get_logger("TCPClientLineSource", "tcp_client_source.log")
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


class BroadcastServer:
    """Pure output server. Listener devices (dashboards, etc.) connect in;
    we push data out to all of them. No inbound data is expected or processed."""

    def __init__(self, host="0.0.0.0", port=65432, max_clients=10):
        self.host = host
        self.port = port
        self.logger = get_logger("BroadcastServer", "broadcast_server.log")
        self.executor = ThreadPoolExecutor(max_workers=max_clients, thread_name_prefix="tcp-client")
        self.clients = {}
        self.clients_lock = threading.Lock()

    def run(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind((self.host, self.port))
                server_socket.listen()
                self.logger.info(f"Broadcasting on {self.host}:{self.port}...")

                while True:
                    client_socket, client_address = server_socket.accept()
                    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    with self.clients_lock:
                        self.clients[client_socket] = client_address
                    self.executor.submit(self._handle_client, client_socket, client_address)

        except Exception:
            self.logger.exception("Error in broadcast server")

    def broadcast(self, data):
        with self.clients_lock:
            targets = list(self.clients.keys())

        for sock in targets:
            try:
                sock.sendall(data)
            except (TimeoutError, ConnectionResetError, BrokenPipeError, OSError):
                self.logger.exception(f"Error broadcasting to {self.clients.get(sock)}")

    def _handle_client(self, client_socket, client_address):
        with client_socket:
            self.logger.info(f"Listener connected: {client_address}")
            try:
                # We don't expect listeners to send anything; just watch for disconnect.
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        self.logger.info(f"Listener {client_address} disconnected.")
                        break
            except (TimeoutError, ConnectionResetError, OSError):
                self.logger.exception(f"Error on listener connection {client_address}")
            finally:
                with self.clients_lock:
                    self.clients.pop(client_socket, None)


class DataCollector:
    def __init__(self, mode="serial", com_port="COM14", baudrate=115200,
                 esp32_host=None, esp32_port=None,
                 broadcast_host="0.0.0.0", broadcast_port=65432):
        assert mode in ("serial", "tcp"), "mode must be 'serial' or 'tcp'"
        self.mode = mode
        self.logger = get_logger("DataCollector", "data_collector.log")
        self.broadcaster = BroadcastServer(host=broadcast_host, port=broadcast_port)

        if mode == "serial":
            self.source = SerialLineSource(com_port=com_port, baudrate=baudrate)
        else:
            assert esp32_host and esp32_port, "esp32_host/esp32_port required for tcp mode"
            self.source = TCPClientLineSource(esp32_host, esp32_port)

    def _consume_source(self):
        """Runs forever: connect, read lines, parse/validate/log, rebroadcast."""
        while True:
            self.source.connect()
            try:
                while True:
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
                        self.broadcaster.broadcast(raw)

                    except Exception:
                        self.logger.exception(f"Error processing data from source ({self.mode})")
                        log_data(['-'] * 12)
            finally:
                self.source.close()

            time.sleep(1)  # brief pause before reconnect loop restarts

    def run(self):
        self.logger.info(f"Data collection supervisor starting in '{self.mode}' mode")
        tasks = [self.broadcaster.run, self._consume_source]

        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(fn): fn for fn in tasks}
            while futures:
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                for future in done:
                    fn = futures.pop(future)
                    try:
                        future.result()
                    except Exception:
                        self.logger.exception(f"{fn.__qualname__} crashed")
                    else:
                        self.logger.info(f"{fn.__qualname__} exited cleanly")

                    time.sleep(1)
                    futures[executor.submit(fn)] = fn


if __name__ == "__main__":
    # USB mode:
    data_collector = DataCollector(mode="serial", com_port="COM14")

    # TCP mode (ESP32 as server, Pi Zero connects out to it):
    # data_collector = DataCollector(mode="tcp", esp32_host="192.168.1.50", esp32_port=65432)

    data_collector.run()