#!/usr/bin/python3
import os
import sys

import serial

UPS_TO_MONITOR = [
    ('/dev/ttyUSB0', 'MyUPS')
]


class Ups:
    def __init__(self, port):
        self.port = port
        self.__connect()

    def __connect(self):
        self.serial = serial.Serial(
            self.port,
            baudrate=2400,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )

    def __command(self, command):
        self.serial.write(bytes(
            f'{command}\r',
            'utf-8'
        ))

        response = self.serial.readline()

        if response[0] != 40:
            raise ValueError('Response malformed')

        return response[1:].decode('utf-8').rstrip()

    def status(self):
        response = self.__command('Q1')

        response = response.split(' ')

        return {
            'input_voltage': response[0],
            'input_fault_voltage': response[1],
            'output_voltage': response[2],
            'output_current_percentage': int(response[3]),
            'input_frequency': response[4],
            'battery_voltage': response[5],
            'temperature': response[6],
            'utility_fail': response[7][0],
            'battery_low': response[7][1],
            'bypass_active': response[7][2],
            'ups_failed': response[7][3],

            # If this is 0 then UPS is on battery and actively providing power
            'ups_in_standby': response[7][4],

            'test_in_progress': response[7][5],
            'shutdown_active': response[7][6],
            'beeper_on': response[7][7]
        }


def main():
    for (port, name) in UPS_TO_MONITOR:
        ups = Ups(port)

        status_json = ups.status()
        status = []

        for key in status_json:
            status.append(f'{key}={status_json[key]}')

        status = ' '.join(status)

        print(f'upses,name={name} {status}')


if __name__ == "__main__":
    sys.exit(main())
