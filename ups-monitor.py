#!/usr/bin/python3
import json
import os
import sys

import requests
import serial
import urllib3

urllib3.disable_warnings()


UPS_TO_MONITOR = [
    ('/dev/ttyUSB0', 'MyUPS')
]

SERVER_USERNAME = 'user'
SERVER_PASSWORD = 'pass'

SERVERS = ['https://example-vcenter.com']

DELAYED_HOSTS = ['127.0.0.1']
DELAYED_VMS = ['vcenter']

SERVER_SESSION_PATH = 'api/session'
SERVER_HOST_PATH = 'api/vcenter/host'
SERVER_VM_PATH = 'api/vcenter/vm'

SLACK_HOOK = 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'


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
            'ups_in_standby': response[7][4],
            'test_in_progress': response[7][5],
            'shutdown_active': response[7][6],
            'beeper_on': response[7][7]
        }


class Server:
    # Login
    def __init__(self, server, username, password):
        self.server = server

        self.sess_addr = server + '/' + SERVER_SESSION_PATH
        self.host_addr = server + '/' + SERVER_HOST_PATH
        self.vm_addr = server + '/' + SERVER_VM_PATH

        r = requests.post(self.sess_addr,
                          auth=(username, password),
                          verify=False)

        # Raise exception if authorization failed
        if 200 > r.status_code > 300:
            raise Exception(f'{server}: failed to authenticate; ({r.status_code}) {r.text}')

        self.auth = r.json()

    # Logout
    def log_out(self):
        requests.delete(self.sess_addr,
                        headers={'vmware-api-session-id': self.auth},
                        verify=False)

    def name(self):
        return self.server

    def get_vms(self):
        r = requests.get(self.vm_addr,
                         headers={'vmware-api-session-id': self.auth},
                         verify=False)

        return r.json()

    def shutdown_vm(self, vm):
        addr = self.vm_addr + '/' + vm['vm'] + '/guest/power?action=shutdown'
        r = requests.post(addr,
                          headers={'vmware-api-session-id': self.auth},
                          verify=False)

        # Raise exception if shutdown failed
        if 200 > r.status_code > 300:
            raise Exception(f'{self.server}: failed to shut down {vm["name"]}; ({r.status_code}) {r.text}')

def post_to_slack(msg):
    msg_obj = {'text': msg}
    requests.post(SLACK_HOOK,
                  headers={'Content-Type': 'application/json'},
                  data=json.dumps(msg_obj))


def main():
    for (port, name) in UPS_TO_MONITOR:
        ups = Ups(port)

        status_json = ups.status()
        status = []

        for key in status_json:
            status.append(f'{key}={status_json[key]}')

        status = ','.join(status)

        print(f'upses,name={name} {status}')

        if status_json['utility_fail'] == '1' and status_json['battery_low'] == '1':
            post_to_slack('UPS power low; shutting down servers')

            for s in SERVERS:
                # Automatically logs into server
                server = Server(s, SERVER_USERNAME, SERVER_PASSWORD)

                vms = server.get_vms()
                delayed_vms = []

                # Shut down VMs
                # Skip if VM is supposed to be delayed
                for vm in vms:
                    if vm['name'] in DELAYED_VMS:
                        delayed_vms.append(vm)
                    elif vm['power_state'] == 'POWERED_ON':
                        server.shutdown_vm(vm)

                # Shut down delayed VMs
                for vm in delayed_vms:
                    server.shutdown_vm(vm)

                server.log_out()

if __name__ == "__main__":
    sys.exit(main())
