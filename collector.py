import serial
import csv
import time

class SerialCollector:

    def __init__(self, port="COM4"):
        self.ser = serial.Serial(baudrate = 115200, port=port)
        self.ser.reset_input_buffer()


    def clean_data(self, data):
        data = data.replace('\n', '').replace('\r', '').split('>')[-1].split(',')

        if len(data) != 10:
            data = ['0']*10

        return data


    def log_data(self, data):
        with open('data_log.csv', mode='a', newline='') as data_log:
            writer = csv.writer(data_log)
            writer.writerow(data)


    def read_data(self):

        while True:
            try:
                raw_data = self.ser.readline().decode('ascii')
                cleaned_data = self.clean_data(raw_data)
                self.log_data(cleaned_data)

            except Exception as e:
                print(f'Error: {e}')
                self.log_data('-,-,-,-,-,-,-,-,-,-')

            self.ser.reset_input_buffer()
            time.sleep(30)


if __name__ == "__main__":
    serial_collector = SerialCollector()
    serial_collector.read_data()
