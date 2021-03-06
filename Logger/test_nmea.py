#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 16:36:01 2021

@author: wmorland
"""

import unittest
from unittest.mock import patch
from unittest.mock import call
import subprocess
import nmea


class TestStartCanBus(unittest.TestCase):
    """Test cases for start_can_bus."""

    @patch('subprocess.run', return_value=0,
           side_effect=subprocess.CalledProcessError(256, 'ip'))
    def test_run_fail(self, ip_call):
        """start_can_bus() ip link set fails"""
        with self.assertLogs(level='ERROR') as logs:
            bus = nmea.start_can_bus()
        ip_call.assert_called_with('sudo ip link set can0 type can '
                                   'bitrate 100000', check=True)
        self.assertEqual(logs.output,
                         ['ERROR:nmea:ip link set can0: FAIL',
                          'ERROR:nmea:return code = 256'],
                         msg='expect ERROR logged when ip link set fails.')
        self.assertIsNone(bus, msg='start_can_bus should return None if '
                          'call to ip link set fails.')

    @patch('subprocess.run')
    def test_run2_fail(self, ip_call):
        """start_can_bus() ifconfig fails"""

        def subprocess_call_behaviour(*args, **kwargs):
            if args[0] == 'sudo ip link set can0 type can bitrate 100000':
                return 0
            raise subprocess.CalledProcessError(256, 'ip')

        ip_call.side_effect = subprocess_call_behaviour
        with self.assertLogs(level='ERROR') as logs:
            bus = nmea.start_can_bus()
        self.assertEqual(logs.output,
                         ['ERROR:nmea:ifconfig can0 up: FAIL',
                          'ERROR:nmea:return code = 256'],
                         msg='expect ERROR logged when ip link set fails.')
        self.assertIsNone(bus, msg='start_can_bus should return None if '
                          'call to ifconfig fails.')

    @patch('subprocess.run', return_value=0)
    @patch('can.interface.Bus')
    def test_sucessful_start(self, can_bus, ip_call):
        """start_can_bus() sucess."""
        bus = nmea.start_can_bus()
        expected_ip_calls = [call('sudo ip link set can0 type can bitrate '
                                  '100000', check=True),
                             call('sudo ifconfig can0 up', check=True)]
        self.assertEqual(ip_call.call_args_list, expected_ip_calls,
                         msg='Expected two successful subprocess calls.')
        self.assertEqual(can_bus.call_args_list,
                         [call(channel='can0', bustype='socketcan_ctypes')],
                         msg='Expected one successful call to create'
                             'can.interface.bus')
        self.assertIsNotNone(bus,
                             msg='start_can_bus should return a Bus object'
                                 'when called successfully')


class TestStopCanBus(unittest.TestCase):
    """Test cases for stop_can_bus."""

    @patch('subprocess.run', return_value=0,
           side_effect=subprocess.CalledProcessError(256, 'ip'))
    def test_run_fail(self, ip_call):
        """stop_can_bus() ifconfig fails"""
        with self.assertLogs(level='ERROR') as logs:
            rc = nmea.stop_can_bus()
            rc = nmea.stop_can_bus()
        ip_call.assert_called_with('sudo ifconfig can0 down', check=True)
        print(logs.output)
#        self.assertEqual(logs.output,
#                         ['ERROR:nmea:ifconfig can0 up: FAIL',
#                          'ERROR:nmea:return code = 256'],
#                         msg='expect ERROR logged when ip link set fails.')
        self.assertIsNone(rc, msg='stop_can_bus should return None if call to'
                          'ifconfig fails.')

    @patch('subprocess.run', return_value=0)
    def test_successful_stop(self, ip_call):
        """stop_can_bus() success"""
        rc = nmea.stop_can_bus()
        ip_call.assert_called_with('sudo ifconfig can0 down', check=True)
        self.assertIsNone(rc, msg='stop_can_bus should return None on '
                          'success.')


class TestSetFilters(unittest.TestCase):
    """Test cases for set_filters."""

    def test_ok(self):
        """Dummy test."""
        self.assertTrue(True, msg='Should always pass.')


class TestGetGpsTime(unittest.TestCase):
    """Test cases for get_gps_time."""

    def test_ok(self):
        """Dummy test."""
        self.assertTrue(True, msg='Should always pass.')


if __name__ == '__main__':
    unittest.main()
