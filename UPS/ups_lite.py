#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 19:51:42 2021

@author: wmorland
"""

from time import sleep
import logging
import warnings
import struct
import smbus
import RPi.GPIO as GPIO


class UPS:

    MAX17040G = 0x36
    VCELL = 0x02
    SOC = 0x04
    MODE = 0x06
    quick_start_cmd = 0x4000
    COMMAND = 0xfe
    power_on_reset_cmd = 0x0054

    def quick_start(self):
        """
        Restart fuel-gauge calculations.

        A quick-start allows the MAX17040 to restart fuel_gauge calculations in
        the same manner as initial power up of the IC. For example if an
        application's power-up sequence is exceedly noisy such that excess
        error introduced into the IC's "first guess" of SOC, the host can issue
        a quick_start to reduce the error.  A quick-start is initiatied by
        writing 0x4000 to the MODE register

        Parameters
        ----------
        bus : smbus.SMBus
            System Management Bus Protocol layer on top of I2C.

        Returns
        -------
        None.

        """
        self.bus.write_word_data(self.MAX17040G, self.MODE,
                                 self.quick_start_cmd)
        sleep(0.1)

    def power_on_reset(self):
        """
        Restart the MAX17040 fuel-gauge.

        Writing a value of 0x0054 to the COMMAND register causes the MAX17040
        to completely reset as if power had been removed.  The reset occurs
        when the last bit has been clocked in.  The IC does not respond with an
        I2C ACK after this command sequence.

        Parameters
        ----------
        bus : smbus.SMBus
            System Management Bus Protocol layer on top of I2C.

        Returns
        -------
        None.

        """
        self.bus.write_word_data(self.MAX17040G, self.COMMAND,
                                 self.power_on_reset_cmd)
        sleep(0.1)

    def __init__(self):
        """
        Initialize status functions for UPS-Lite.

        Returns
        -------
        None.

        """
        try:
            GPIO.setmode(GPIO.BCM)
        except ValueError:
            logging.error('Unable to set GPIO Mode to BCM.')
            raise Exception()
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            try:
                GPIO.setup(4, GPIO.IN)
            except Exception:
                logging.error('GPIO pin 4 is already in use.')
                raise Exception()
        self.bus = smbus.SMBus(1)
        # 0 = /dev/i2c-0 (port I2C0)
        # 1 = /dev/i2c-1 (port I2C1)

        self.power_on_reset()
        self.quick_start()

    def voltage(self):
        """
        UPS battery voltage.

        Battery voltage is measured at the CELL pin input with respect to GND
        over a 0 to 5.00V range for the MAX17040 with a resolution of 1.25mV.
        The A/D calculates the average cell voltage for a period of 125ms after
        IC power on reset and then for a period of 500ms for every cycle
        afterwards.  The result is placed in the VCELL register at the end of
        each conversion period.

        Parameters
        ----------
        bus : smbus.SMBus
            System Management Bus Protocol layer on top of I2C.

        Returns
        -------
        voltage : float
            Voltage from MAX17040G on UPS-Lite.

        """
        read = self.bus.read_word_data(self.MAX17040G, self.VCELL)
        # swap hi and lo bytes
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        # convert to decimal volts
        voltage = swapped * 1.25 / 1000 / 16
        return voltage

    def capacity(self):
        """
        UPS-Lite battery state of charge.

        The SOC register is a read-only register that displays the state of
        charge of the cell as calculated by the ModelGauge algorithm.  The
        result is displayed as a percentage of the cell's full capacity.
        This register automatically adapts to variation in battery size since
        the MAX17040 naturally recognizes relative SOC.  Units of % can be
        directly determined by observing only the high byte of the register.
        The low byte provides additional resolution in units 1/256%.  The
        reported SOC also includes residual capacity that might not be
        available to the application because of early termination voltage
        requirements.  When SOC = 0, typical applications have no remaining
        capacity.

        The first update occurs within 250ms after IC power on reset.
        Subsequent updates occur at variable intervals depending on application
        conditions.  ModelGauge calculations outside the register are clamped
        at minimum and maximum register limits.

        Parameters
        ----------
        bus : smbus.SMBus
            System Management Bus Protocol layer on top of I2C.

        Returns
        -------
        capacity : float
            State of charge of the UPS-Lite battery. 0% to 100%

        """
        read = self.bus.read_word_data(self.MAX17040G, self.SOC)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        capacity = swapped / 256
        return capacity

    def external_power(self):
        """
        State of external power.

        Returns
        -------
        Boolean
            State of external power, True if connected to external power.
        """
        if GPIO.input(4) == GPIO.HIGH:
            return True
        if GPIO.input(4) == GPIO.LOW:
            return False
