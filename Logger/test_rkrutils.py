#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 20:14:14 2021

@author: wmorland
"""

import unittest
from unittest.mock import patch
import zipfile
import rkrutils
import subprocess


class TestZipLogs(unittest.TestCase):
    """Test cases for zip_logs."""

    @patch('os.listdir', return_value=[])
    @patch('zipfile.ZipFile')
    def test_empty_directory(self, zip_file, list_dir):
        """zip_logs() no files in directory."""
        rkrutils.zip_logs()
        self.assertEqual(zip_file.call_args_list, [],
                         msg='Should not attempt to zip when no files in '
                         'directory.')

    @patch('os.listdir', return_value=['log.txt'])
    @patch('zipfile.ZipFile')
    def test_no_file_match(self, zip_file, list_dir):
        """zip_logs() no *.n2k files in directory."""
        rkrutils.zip_logs()
        self.assertEqual(zip_file.call_args_list, [],
                         msg='Should not attempt to zip when no *.n2k files '
                         'in directory.')

    @patch('os.listdir', return_value=['log.n2k'])
    @patch('zipfile.ZipFile.__init__', autospec=True,
           side_effect=zipfile.BadZipFile())
#    @patch('zipfile.ZipFile.testzip', return_value=None)
    def test_one_bad_file(self, zip_file, list_dir):
        """zip_logs() one bad *.n2k file in directory."""
        with self.assertLogs(level='ERROR') as logs:
            rkrutils.zip_logs()
        # self.assertEqual(zip_file.call_args_list,
        #                  [call('./log.n2k.zip', 'w')],
        #                  msg='Expected one call to create zip file.')
        self.assertEqual(logs.output,
                         ['ERROR:rkrutils:Zipping log.n2k into log.n2k.zip: '
                          'FAIL'],
                         msg='expect ERROR logged when zip file create fails.')


class TestSendToUSB(unittest.TestCase):
    """Test cases for send_to_drive."""

    def test_ok(self):
        """Dummy test."""
        self.assertTrue(True, msg='Should always pass.')

    @patch('os.getenv', return_value='/media/usb')
    @patch('os.path.ismount', return_value=False)
    @patch('subprocess.run',
           side_effect=subprocess.CalledProcessError(32, 'cmd'))
    def test_no_usb(self, mock_run, mock_ismount, mock_env):
        """USB drive not mounted and not mountable."""
        with self.assertLogs(level='WARNING') as logs:
            rkrutils.send_to_usb()
        mock_env.assert_called_once_with('USBDRIVE')
        mock_ismount.assert_called_once_with('/media/usb')
        mock_run.assert_called_once_with(['sudo', 'mount', '/dev/sda1',
                                          '/media/usb', '-o', 'uid=pi,gid=pi'],
                                         check=True)
        self.assertEqual(logs.output,
                         ['WARNING:rkrutils:USB drive not mounted at '
                          '/media/usb',
                          'WARNING:root:Mount USB drive return code = 32: '
                          'FAIL'],
                         msg='expect WARNING logged when drive not mounted')

    @patch('os.getenv', return_value='/media/usb')
    @patch('os.path.ismount', side_effect=[False, True])
    @patch('subprocess.run', return_value=0)
    @patch('shutil.move')
    def test_usb_not_mounted(self, mock_move, mock_run, mock_ismount,
                             mock_env):
        """USB drive not mounted, mount succeeds."""
        with self.assertLogs(level='WARNING') as logs:
            rkrutils.send_to_usb()
        self.assertEqual(logs.output,
                         ['WARNING:rkrutils:USB drive not mounted at '
                          '/media/usb'],
                         msg='expect WARNING logged when drive not mounted')


if __name__ == '__main__':
    unittest.main()
