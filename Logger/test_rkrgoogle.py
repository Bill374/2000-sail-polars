#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 20:14:14 2021

@author: wmorland
"""

import unittest


class TestSendToDrive(unittest.TestCase):
    """Test cases for send_to_drive."""

    def test_ok(self):
        """Dummy test."""
        self.assertTrue(True, msg='Should always pass.')


if __name__ == '__main__':
    unittest.main()
