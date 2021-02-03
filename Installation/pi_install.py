#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 21:24:52 2021

@author: wmorland
"""

import logging


class CfgLine:
    """
    Line to add to a config file.
    The boolean found indicate if the line is already in the file.
    """

    def __init__(self, line):
        self.line = line
        self.found = False

    def __str__(self):
        output = self.line
        if self.found:
            output = output + ', True'
        else:
            output = output + ', False'
        return output


def add_lines(file_name, lines):
    """
    Append lines to the end of a text file.

    Each line will only be appended if it is not already found in the file.
    If the file is not found or cannot be opened an error is logged, but no
    error code is returned.

    Parameters:
        file_name (str): The full path and name of the file to edited
        lines (list): The lines to be added to the file

    Returns:
        No return value
    """
    if lines is None:
        logging.error(f'No lines given to be added to {file_name}')
        return
    logging.info(f'Reading {file_name}, checking if updates required.')
    try:
        file_to_edit = open(file_name, 'r')
    except IOError:
        logging.error(f'Cannot open {file_name} for read')
        return
    for source in file_to_edit:
        for target in lines:
            if source == target.line:
                logging.info('Found ' + target.line.strip('\n'))
                target.found = True
    file_to_edit.close()

    # Are there any lines to be added to file_name?
    need_update = False
    for target in lines:
        if not target.found:
            need_update = True

    if need_update:
        logging.info(f'Writing to {file_name}')
        try:
            file_to_edit = open(file_name, 'a')
        except IOError:
            logging.error(f'Cannot open {file_name} for write')
            return
        file_to_edit.write('\n# RKR Logger\n')
        for target in lines:
            if not target.found:
                logging.info('Writing ' + target.line.strip('\n'))
                file_to_edit.write(target.line)
        file_to_edit.close()
        logging.info(f'Finished modifying {file_name}')
    else:
        logging.info(f'No updates needed to {file_name}')
