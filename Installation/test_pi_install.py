#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 19:59:53 2021

@author: wmorland
"""

import unittest
from unittest.mock import patch
from unittest.mock import mock_open
from unittest.mock import call
import pi_install as pi


class TestAddLines(unittest.TestCase):

    def test_bad_file(self):
        """add_lines called with a file_name that cannot be opened."""
        test_lines = [pi.CfgLine('first line')]
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError()
            with self.assertLogs(level='ERROR') as logs:
                pi.add_lines('no_file', test_lines)

        mock_file.assert_called_with('no_file', 'r')
        self.assertEqual(logs.output,
                         ['ERROR:root:Cannot open no_file for read'],
                         msg='expect ERROR logged when file cannot be opened')

    def test_no_lines(self):
        """add_lines called with no lines to be added to the file."""
        with patch("builtins.open", mock_open()):
            with self.assertLogs(level='ERROR') as logs:
                pi.add_lines('no_file', None)
        self.assertEqual(logs.output,
                         ['ERROR:root:No lines given to be added to no_file'],
                         msg='expect ERROR logged when no lines to be added')

    def test_lines_in_file(self):
        """
        add_lines called when all lines to be added are already in the file.
        """
        file_contents = ("first line\n"
                         "second line\n"
                         "third line\n")
        test_lines = [pi.CfgLine("second line\n")]
        with patch("builtins.open",
                   mock_open(read_data=file_contents)) as test_file:
            with self.assertLogs(level="INFO") as logs:
                pi.add_lines('test_file', test_lines)
        self.assertEqual(logs.output,
                         ['INFO:root:Reading test_file, '
                          'checking if updates required.',
                          'INFO:root:Found second line',
                          'INFO:root:No updates needed to test_file'],
                         msg='expect no lines to be written to file')
        handle = test_file()
        handle.write.assert_not_called()

    @unittest.skip("need to mock throw exception on write")
    def test_cannot_write_file(self):
        """
        add_lines called on with a file that cannont be opened for write.
        """
        file_contents = ("first line\n")
        test_lines = [pi.CfgLine("second line\n")]
        with patch("builtins.open",
                   mock_open(read_data=file_contents)) as test_file:
            with self.assertLogs(level="ERROR") as logs:
                pi.add_lines('test_file', test_lines)
        self.assertEqual(logs.output,
                         ['ERROR:root:Cannot open test_file for write'],
                         msg='expect ERROR logged when file cannot be opened '
                         'for write')

    def test_one_line(self):
        """
        add_lines called successfully with a single line to be added.
        """
        file_contents = ("first line\n")
        test_lines = [pi.CfgLine("second line\n")]
        with patch("builtins.open",
                   mock_open(read_data=file_contents)) as test_file:
            pi.add_lines('test_file', test_lines)
        handle = test_file()
        calls = [call('\n# RKR Logger\n'),
                 call('second line\n')]
        handle.write.assert_has_calls(calls)

    def test_two_lines_write_one(self):
        """
        add_lines called successfully with two lines one succesffully added.
        """
        file_contents = ("first line\n"
                         "second line\n")
        test_lines = [pi.CfgLine("second line\n"),
                      pi.CfgLine("third line\n")]
        with patch("builtins.open",
                   mock_open(read_data=file_contents)) as test_file:
            pi.add_lines('test_file', test_lines)
        handle = test_file()
        calls = [call('\n# RKR Logger\n'),
                 call('third line\n')]
        handle.write.assert_has_calls(calls)

# lines has two lines - both are successfully written to file
    def test_two_lines_write_two(self):
        """
        add_lines called successfully with two lines one succesffully added.
        """
        file_contents = ("first line\n")
        test_lines = [pi.CfgLine("second line\n"),
                      pi.CfgLine("third line\n")]
        with patch("builtins.open",
                   mock_open(read_data=file_contents)) as test_file:
            pi.add_lines('test_file', test_lines)
        handle = test_file()
        calls = [call('\n# RKR Logger\n'),
                 call('second line\n'),
                 call('third line\n')]
        handle.write.assert_has_calls(calls)


if __name__ == '__main__':
    unittest.main()
