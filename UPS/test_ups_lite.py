#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 19:24:20 2021

@author: wmorland
"""

import unittest
from unittest.mock import patch
import RPi.GPIO as GPIO
import ups_lite


class TestVoltage(unittest.TestCase):
    """Test cases for read_voltage."""

    def test_ok(self):
        """Dummy test."""
        self.assertTrue(True, msg='Should always pass.')


class TestCapacity(unittest.TestCase):
    """Test cases for read_capacity."""

    def test_ok(self):
        """Dummy test."""
        self.assertTrue(True, msg='Should always pass.')


class TestQuickStart(unittest.TestCase):
    """Test cases for quick_start."""

    def test_ok(self):
        """Dummy test."""
        self.assertTrue(True, msg='Should always pass.')


class TestPowerOnReset(unittest.TestCase):
    """Test cases for power_on_reset."""

    def test_ok(self):
        """Dummy test."""
        self.assertTrue(True, msg='Should always pass.')


class TestInit(unittest.TestCase):
    """Test cases for __init__."""

    @patch('RPi.GPIO.setmode', side_effect=ValueError())
    def test_fail_gpio_mode(self, gpio_mock):
        """Conflicting GPIO mode."""
        with self.assertLogs(level='ERROR') as logs:
            self.assertRaises(Exception, ups_lite.UPS(),
                              msg='Exception should be raised if GPIO setmode '
                              'fails.')
        gpio_mock.assert_called_with(GPIO.BCM)
        self.assertEqual(logs.output,
                         ['ERROR:root:Unable to set GPIO Mode to BCM.'],
                         msg='Expect ERROR logged when GPIO.setmode fails.')

    @patch('RPi.GPIO.setmode')
    @patch('RPi.GPIO.setup', side_effect=RuntimeWarning())
    def test_fail_pin_4(self, gpio_mock_setup, gpio_mock_setmode):
        """Conflicting setup for GPIO Pin 4."""
        with self.assertLogs(level='ERROR') as logs:
            self.assertRaises(Exception, ups_lite.UPS(),
                              msg='Exception should be raised if GPIO setup '
                              'fails.')
        gpio_mock_setmode.assert_called_with(GPIO.BCM)
        gpio_mock_setup.assert_called_with(4, GPIO.IN)
        self.assertEqual(logs.output,
                         ['ERROR:root:GPIO pin 4 is already in use.'],
                         msg='Expect ERROR logged when GPIO.setmode fails.')

    def test_ok(self):
        """Successful initialization."""
        ups = ups_lite.UPS()
        self.assertTrue(type(ups) is ups_lite.UPS,
                        msg='Successful initiation should return ups-lite.UPS')
        self.assertEqual(GPIO.getmode(), GPIO.BCM,
                         msg='GPIO should be set to Broadcom numbering.')
        self.assertEqual(GPIO.gpio_function(4), GPIO.IN,
                         msg='GPIO Pin 4 should be set to input.')
        self.assertEqual(ups.MAX17040G, 0x36,
                         msg='I2C address of MAX17040G should be 0x36')
        self.assertEqual(ups.VCELL, 0x02,
                         msg='VCELL register address should be 0x02')
        self.assertEqual(ups.SOC, 0x04,
                         msg='SOC register address should be 0x04')
        self.assertEqual(ups.MODE, 0x06,
                         msg='MODE register address should be 0x06')
        self.assertEqual(ups.quick_start_cmd, 0x4000,
                         msg='MODE register quick-start command should be '
                         '0x4000')
        self.assertEqual(ups.COMMAND, 0xfe,
                         msg='COMMAND register address should be 0xfe')
        self.assertEqual(ups.power_on_reset_cmd, 0x0054,
                         msg='COMMAND register power-on reset command should '
                         'be 0x0054')


class TestExternalPower(unittest.TestCase):
    """Test cases for external_power."""

    @patch('ups_lite.UPS.__init__', return_value=None)
    @patch('RPi.GPIO.input', return_value=GPIO.HIGH)
    def test_external_power_on(self, gpio_mock, ups_mock):
        """External power connected."""
        ups = ups_lite.UPS()
        self.assertTrue(ups.external_power(), msg='Expect power on when GPIO '
                        'pin 4 is HIGH')
        gpio_mock.assert_called_with(4)

    @patch('ups_lite.UPS.__init__', return_value=None)
    @patch('RPi.GPIO.input', return_value=GPIO.LOW)
    def test_external_power_off(self, gpio_mock, ups_mock):
        """External power connected."""
        ups = ups_lite.UPS()
        self.assertTrue(not ups.external_power(), msg='Expect power off when '
                        'GPIO pin 4 is LOW')
        gpio_mock.assert_called_with(4)


if __name__ == '__main__':
    unittest.main()
