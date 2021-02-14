#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 21:24:52 2021

@author: wmorland
"""

import logging
import os
import wget
import urllib3
import configparser


def install_python_modules():
    """
    Install required python modules listed in install.cfg.

    Returns
    -------
    rc : int
         0 : successful
        -1 : error

    """
    logging.basicConfig(level=logging.INFO)
    config = configparser.ConfigParser()
    config.read('install.cfg')

    try:
        python_modules = config.get('PYTHON', 'modules')
    except configparser.NoSectionError:
        logging.error('PYTHON section missing from install.cfg')
        return -1
    except configparser.NoOptionError:
        logging.error('No list of PYTHON modules found in install.cfg')
        return -1

    module_list = python_modules.splitlines(False)
    module_list = list(filter(None, module_list))

    for module in module_list:
        logging.info(f'Installing Python module {module}.')
        rc = os.system(f'pip3 install --upgrade {module}')
        if not rc:
            logging.info(f'Installing Python module {module}: SUCCESS')
        else:
            logging.error(f'Installing Python module {module}: FAIL')
            return -1
        print(f'pip install --upgrade {module}')
        print(f'Return code: {rc}')

    return 0


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


def main(git_hub_url):
    """
    Main installation function.

    Returns
    -------
    None.

    """
    logging.info('*** Start main-install ***')

    directory = os.getcwd()

    logging.info(f'installing from {git_hub_url}')
    logging.info(f'installing to {directory}')

    # download all the files listed in the manifest file
    logging.info('Retrieving manifest of files to install')
    fileName = wget.download(f'{git_hub_url} Installation/manifest.txt')
    logging.info('')
    logging.info(f'downloaded {fileName}')
    manifest = open('manifest.txt', 'r')
    http = urllib3.PoolManager()
    for source in manifest:
        if source[0] != '#':
            fileToGet = git_hub_url + source.strip('\n')
            try:
                req = http.request('GET', fileToGet)
            except urllib3.exceptions.HTTPError as http_error:
                logging.info('unable to find file ' + source.strip('\n') +
                             ' listed in manifest')
                logging.info(http_error)
                return 3
            fileName = wget.download(fileToGet, out=directory)
            logging.info('')
            logging.info('downloaded ' + fileName)
    manifest.close()

    # install apt dependencies
    logging.inf('Installing apt dependencies')
    rc = os.system('apt-get update')
    if rc != 0:
        logging.error('apt-get update failed.')

    # Controller Area Network utilities
    rc = os.system('apt-get install -y can-utils')
    if rc != 0:
        logging.error('apt-get install can-untils failed.')

    # I2C tools for UPS HAT
    rc = os.system('apt-get install i2c-tools')
    if rc != 0:
        logging.error('apt-get install i2c-tools failed.')

    # install python packages
    rc = install_python_modules()
    if not rc:
        logging.info('Python modules successully installed.')
    else:
        logging.error('Error installing python modules.')

    # modify /boot/config.txt if required
    bootCfg = []
    bootCfg.append(CfgLine('# Waveshare RS485 CAN HAT mcp2515 kernel '
                           'driver\n'))
    bootCfg.append(CfgLine('dtparam=spi=on\n'))
    # RS485 CAN HAT - 12M crystal version
    bootCfg.append(CfgLine('dtoverlay=mcp2515-can0,oscillator=12000000,'
                           'interrupt=25,spimaxfrequency=2000000\n'))
    add_lines('/boot/config.txt', bootCfg)

    logging.info('*** End main-install ***')
    return 0
