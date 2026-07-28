import serial # type: ignore
import socket
import os
from time import sleep
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

from utils import clean_data, log_data
from event_logger import get_logger


class SerialCollector:
    def __init__(self, com_port="/dev/aqs-sensor", baudrate=115200, polling_interval=30):
        self.com_port = com_port
        self.baudrate = baudrate
        self.polling_interval = polling_interval
        self.logger = get_logger("SerialCollector", "serial_collector.log")

    def run(self):
        already_warned = False
        while True:
            if not os.path.exists(self.com_port):
                if not already_warned:
                    self.logger.warning(f"Serial device {self.com_port} not found, waiting silently")
                    already_warned = True
                sleep(1)
                continue
            
            try:
                with serial.Serial(self.com_port, self.baudrate, timeout=1) as ser:
                    while True:
                        sleep(self.polling_interval)

                        try:
                            raw_data = ser.readline().decode('ascii')
                            cleaned_data = clean_data(raw_data)
                            if not cleaned_data:
                                continue

                            log_data(cleaned_data)
                            self.logger.debug(f"Data received from serial port {self.com_port}: {cleaned_data}")

                        except Exception as e:
                            self.logger.exception(f"Error while reading from serial port {self.com_port}")
                            log_data(['-']*12)

                            
                        ser.reset_input_buffer()

            except serial.SerialException:
                self.logger.exception(f"Error while opening serial port {self.com_port}")
                sleep(1)  # Wait before retrying to open the serial port


class TCPCollector:
    def __init__(self, host="0.0.0.0", port=65432):
        self.host = host
        self.port = port
        self.logger = get_logger("TCPCollector", "tcp_collector.log")

    def run(self):
        try: 
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind((self.host, self.port))
                server_socket.listen()
                self.logger.info(f"Server is listening on {self.host}:{self.port}...")

                while True:
                    client_socket, client_address = server_socket.accept()
                    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                    with client_socket:
                        self.logger.info(f"Connected successfully to client: {client_address}")
                        while True:
                            try:
                                data = client_socket.recv(1024)
                            except (TimeoutError, ConnectionResetError):
                                self.logger.exception(f"Error while receiving data from client {client_address}")
                                break

                            if not data:
                                self.logger.info(f"Client {client_address} disconnected.")
                                break

                            try:
                                decoded_data = data.decode('ascii')
                                cleaned_data = clean_data(decoded_data)
                                if not cleaned_data:
                                    continue

                                log_data(cleaned_data)
                                self.logger.debug(f"Data received from client {client_address}: {cleaned_data}")

                            except Exception:
                                self.logger.exception(f"Error while processing data from client {client_address}")
                                log_data(['-']*12)

        except Exception:
            self.logger.exception(f"Error in TCP server")

            
class DataCollector:

    def __init__(self, polling_interval=30):
        self.serial_collector = SerialCollector(polling_interval=polling_interval)
        self.tcp_collector = TCPCollector()
        self.polling_interval = polling_interval
        self.logger = get_logger("DataCollector", "data_collector.log")

    def run(self):
        self.logger.info("Data collection supervisor starting")

        tasks = {
            self.serial_collector.run: None,
            self.tcp_collector.run: None,
        }
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(fn): fn for fn in tasks}
            while futures:
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                for future in done:
                    fn = futures.pop(future)
                    try:
                        future.result()
                    except Exception as e:
                        self.logger.exception(f"{fn.__qualname__} crashed")
                    else:
                        self.logger.info(f"{fn.__qualname__} exited cleanly")

                    sleep(1)
                    futures[executor.submit(fn)] = fn

                    
if __name__ == "__main__":
    data_collector = DataCollector()
    data_collector.run()
