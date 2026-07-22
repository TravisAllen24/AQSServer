import serial
import time

from utils import clean_data, log_data

class SerialCollector:

    def __init__(self, port="/dev/aqs-sensor"):
        self.ser = serial.Serial(baudrate = 115200, port=port)
        self.ser.reset_input_buffer()


    def read_data(self):

        while True:
            try:
                raw_data = self.ser.readline().decode('ascii')
                cleaned_data = clean_data(raw_data)
                if not cleaned_data:
                   continue
                
                log_data(cleaned_data)

            except Exception as e:
                print(f'Error: {e}')
                log_data(['-']*12)

            self.ser.reset_input_buffer()
            time.sleep(30)


if __name__ == "__main__":
    serial_collector = SerialCollector()
    serial_collector.read_data()
