#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 16:36:01 2021

@author: wmorland
"""

import unittest
from unittest.mock import patch
from unittest.mock import call
import nmea


class TestStartCanBus(unittest.TestCase):
    """Test cases for start_can_bus."""

    @patch('subprocess.call', return_value=-1)
    def test_call_interupt(self, ip_call):
        """start_can_bus() ip link set terminated by interupt"""
        with self.assertLogs(level='ERROR') as logs:
            bus = nmea.start_can_bus()
        ip_call.assert_called_with('sudo ip link set can0 type can '
                                   'bitrate 100000')
        self.assertEqual(logs.output,
                         ['ERROR:root:Call to ip link set terminated by '
                          'signal.'],
                         msg='expect ERROR logged when ip link set terminated '
                         'by signal.')
        self.assertIsNone(bus, msg='start_can_bus should return None if '
                          'call to ip link set is interupted.')

    @patch('subprocess.call', return_value=0, side_effect=OSError())
    def test_call_fail(self, ip_call):
        """start_can_bus() ip link set fails"""
        with self.assertLogs(level='ERROR') as logs:
            bus = nmea.start_can_bus()
        ip_call.assert_called_with('sudo ip link set can0 type can '
                                   'bitrate 100000')
        self.assertEqual(logs.output,
                         ['ERROR:root:Call to ip link set failed.'],
                         msg='expect ERROR logged when ip link set fails.')
        self.assertIsNone(bus, msg='start_can_bus should return None if '
                          'call to ip link set fails.')

    @patch('subprocess.call', side_effect=[0, -1])
    def test_call2_interupt(self, ip_call):
        """start_can_bus() ifconfig can0 up terminated by interupt"""
        with self.assertLogs(level='ERROR') as logs:
            bus = nmea.start_can_bus()
        ip_call.assert_called_with('sudo ifconfig can0 up')
        self.assertEqual(logs.output,
                         ['ERROR:root:Call to ifconfig terminated by signal.'],
                         msg='expect ERROR logged when ifconfig terminated '
                         'by signal.')
        self.assertIsNone(bus, msg='start_can_bus should return None if '
                          'call to ifconfig is interupted.')

    @patch('subprocess.call')
    def test_call2_fail(self, ip_call):
        """start_can_bus() ifconfig fails"""

        def subprocess_call_behaviour(*args, **kwargs):
            if args[0] == 'sudo ip link set can0 type can bitrate 100000':
                return 0
            raise OSError()

        ip_call.side_effect = subprocess_call_behaviour
        with self.assertLogs(level='ERROR') as logs:
            bus = nmea.start_can_bus()
        self.assertEqual(logs.output,
                         ['ERROR:root:Call to ifconfig failed.'],
                         msg='expect ERROR logged when ip link set fails.')
        self.assertIsNone(bus, msg='start_can_bus should return None if '
                          'call to ifconfig fails.')

    @patch('subprocess.call', return_value=0)
    @patch('can.interface.Bus')
    def test_sucessful_start(self, can_bus, ip_call):
        """start_can_bus() sucess."""
        bus = nmea.start_can_bus()
        expected_ip_calls = [call('sudo ip link set can0 type can bitrate '
                                  '100000'),
                             call('sudo ifconfig can0 up')]
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

    def test_ok(self):
        """Dummy test."""
        self.assertTrue(True, msg='Should always pass.')


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


class TestZipLogs(unittest.TestCase):
    """Test cases for zip_logs."""

    def test_ok(self):
        """Dummy test."""
        self.assertTrue(True, msg='Should always pass.')

    @patch('os.listdir', return_value=[])
    @patch('zipfile.ZipFile')
    def test_empty_directory(self, zip_file, list_dir):
        """zip_logs() no files in directory."""
        nmea.zip_logs()
        self.assertEqual(zip_file.call_args_list, [],
                         msg='Should not attempt to zip when no files in '
                         'directory.')

    @patch('os.listdir', return_value=['log.txt'])
    @patch('zipfile.ZipFile')
    def test_no_file_match(self, zip_file, list_dir):
        """zip_logs() no *.n2k files in directory."""
        nmea.zip_logs()
        self.assertEqual(zip_file.call_args_list, [],
                         msg='Should not attempt to zip when no *.n2k files in '
                         'directory.')

    @patch('os.listdir', return_value=['log.n2k'])
    @patch('zipfile.ZipFile')
    def test_one_file_match(self, zip_file, list_dir):
        """zip_logs() one *.n2k file in directory."""
        nmea.zip_logs()
        self.assertEqual(zip_file.call_args_list,
                         [call('log.n2k.zip', 'w')],
                         msg='Expected one successful call to create zip '
                         'file.')


class TestSendToDrive(unittest.TestCase):
    """Test cases for send_to_drive."""

    def test_ok(self):
        """Dummy test."""
        self.assertTrue(True, msg='Should always pass.')


if __name__ == '__main__':
    unittest.main()
