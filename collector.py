import serial
import socket
from time import sleep

from utils import clean_data, log_data


class SerialCollector:
    def __init__(self, com_port="/dev/aqs-sensor", baudrate=115200):
        try:
            self.ser = serial.Serial(com_port, baudrate, timeout=1)
            sleep(2)  # Wait for the serial connection to initialize
        except serial.SerialException as e:
            print(f"Error initializing serial connection: {e}")
            self.ser = None

    def read_data(self):
        if self.ser is not None:
            try:
                raw_data = self.ser.readline().decode('ascii')
                cleaned_data = clean_data(raw_data)
                if not cleaned_data:
                    return
                log_data(cleaned_data)

            except Exception as e:
                print(f'Error: {e}')
                log_data(['-']*12)

            self.ser.reset_input_buffer()

    def close(self):
        if self.ser is not None:
            self.ser.close()
            self.ser = None


class TCPCollector:
    def __init__(self, host="127.0.0.1", port=8400):
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect((host, port))
        except socket.error as e:
            print(f"Error initializing TCP connection: {e}")
            self.tcp_socket = None

    def read_data(self):
        # Placeholder for TCP reading logic
        if self.tcp_socket is not None:
            try:
                raw_data = self.tcp_socket.recv(4096).decode('ascii')
                cleaned_data = clean_data(raw_data)
                if not cleaned_data:
                    return

                log_data(cleaned_data)
            except Exception as e:
                print(f'Error: {e}')
                log_data(['-']*12)

    def close(self):
        if self.tcp_socket is not None:
            self.tcp_socket.close()
            self.tcp_socket = None


class DataCollector:

    def __init__(self, polling_interval=30):
        self.serial_collector = SerialCollector()
        self.tcp_collector = TCPCollector()
        self.polling_interval = polling_interval

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.serial_collector.close()
        self.tcp_collector.close()

    def start_collection(self):
        while True:
            self.serial_collector.read_data()
            self.tcp_collector.read_data()
            sleep(self.polling_interval)


if __name__ == "__main__":
    with DataCollector() as data_collector:
        data_collector.start_collection()
