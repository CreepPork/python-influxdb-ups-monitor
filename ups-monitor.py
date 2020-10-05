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

        return response


def main():
    for (port, name) in UPS_TO_MONITOR:
        ups = Ups(port)

        text = 'data={}'.format(ups.status())

        print('power-statuses,{}'.format(text))


if __name__ == "__main__":
    sys.exit(main())
