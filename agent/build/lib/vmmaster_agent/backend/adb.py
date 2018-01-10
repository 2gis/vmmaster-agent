# coding: utf-8

import io
import os
import time
import logging
import tempfile
import subprocess

CHECK_CONNECTION_PERIOD = 10
log = logging.getLogger(__name__)


# TODO: Впилить обработку return code и перехват ошибок adb в сам adb_command


class AdbProcess(object):
    def __init__(self, args):
        self.returncode = None

        self._out_tempfile = tempfile.NamedTemporaryFile(delete=True)
        self._err_tempfile = tempfile.NamedTemporaryFile(delete=True)

        self.stdout = open(self._out_tempfile.name, 'rb')
        self.stderr = open(self._err_tempfile.name, 'rb')

        self._process = subprocess.Popen(
            args,
            stdout=self._out_tempfile,
            stderr=self._err_tempfile,
            env=os.environ.copy()
        )

    def __del__(self):
        self.stdout.close()
        self.stderr.close()
        self._out_tempfile.close()
        self._err_tempfile.close()

    def wait(self, timeout=600):
        self.returncode = self._process.wait(timeout)
        return self.returncode

    def poll(self):
        self.returncode = self._process.poll()
        return self.returncode

    def terminate(self):
        self._process.terminate()


def adb_command(driver, params, ping=True, wait=True):
    device_name = get_device_name()

    if not device_connected_yet(device_name):
        raise IOError('ADB connection has been lost for {}'.format(device_name))

    adbp = _exec_adb(device_name, params)
    if ping:
        driver.is_ime_active()
    if wait:
        adbp.wait()
    return adbp


def _exec_adb(device_name, params):
    command = ["adb"] + params
    if device_name:
        command.extend(['-s', device_name])
    log.debug('ADB :{}: {}'.format(device_name, ' '.join(command)))
    return AdbProcess(command)


def get_device_name():
    adbp = _exec_adb(None, ['devices'])
    adbp.wait()
    stdout = adbp.stdout.read()
    log.debug('Connected devices: {}'.format(stdout))
    return stdout


def get_device_state(device_name):
    adbp = _exec_adb(device_name, ['get-state'])
    adbp.wait()
    stdout = adbp.stdout.read()
    log.debug('ADB got state of device {}: {}'.format(device_name, stdout))
    return stdout


def device_connected_yet(device_name):
    is_connected = False
    start_time = time.time()
    while True:
        time.sleep(0.5)
        if time.time() - start_time >= CHECK_CONNECTION_PERIOD:
            log.debug('ADB Connection timeout for device connection check {}'.format(device_name))
            break
        state = get_device_state(device_name)
        if state == 'device\n':
            log.debug('Device {} is connected yet by adb'.format(device_name))
            is_connected = True
            break

    return is_connected
