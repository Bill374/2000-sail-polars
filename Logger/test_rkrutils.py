#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 20:14:14 2021

@author: wmorland
"""

import unittest
from unittest.mock import patch
from unittest.mock import call
import zipfile
import rkrutils


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
    @patch('zipfile.ZipFile', side_effect=zipfile.BadZipFile())
#    @patch('zipfile.ZipFile.testzip', return_value=None)
    def test_one_bad_file(self, zip_file, list_dir):
        """zip_logs() one bad *.n2k file in directory."""
        with self.assertLogs(level='ERROR') as logs:
            rkrutils.zip_logs()
        self.assertEqual(zip_file.call_args_list,
                         [call('log.n2k.zip', 'w')],
                         msg='Expected one call to create zip file.')
        self.assertEqual(logs.output,
                         ['ERROR:rkrutils:Zipping log.n2k into log.n2k.zip: '
                          'FAIL'],
                         msg='expect ERROR logged when zip file create fails.')


class TestSendToDrive(unittest.TestCase):
    """Test cases for send_to_drive."""

    def test_ok(self):
        """Dummy test."""
        self.assertTrue(True, msg='Should always pass.')


if __name__ == '__main__':
    unittest.main()
