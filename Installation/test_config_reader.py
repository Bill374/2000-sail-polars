#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 09:36:19 2021

@author: wmorland
"""

import logging
import configparser
import os
import wget


def copy_files(git_hub_url, install_directory, option):
    """
    Copy files from GitHub to the Pi.

    Parameters
    ----------
    git_hub_url : str
        Complete URL to the raw files in GitHub.
        Must include both the repository and the branch
    install_directory : str
        Full path to the directory on the Pi to save the files
    option : str
        The option in the FILES section of install.cfg that lists the files to
        be copied.

    Returns
    -------
    rc : int
         0 : successful
        -1 : error

    """
    config = configparser.ConfigParser()
    config.read('install.cfg')

    try:
        files = config.get('FILES', option)
    except configparser.NoSectionError:
        logging.error('FILES section missing from install.cfg')
        return -1
    except configparser.NoOptionError:
        logging.error(f'No list of {option} files found in install.cfg')
        return -1

    file_list = files.splitlines(False)
    file_list = list(filter(None, file_list))

    for file in file_list:
        logging.info(f'Copying {file}')
        fileToGet = f'{git_hub_url}{file}'
        try:
            fileName = wget.download(fileToGet, out=directory)
        except wget.HTTPError as http_error:
            logging.error(f'Copying {file}: FAIL')
            logging.error(http_error)
            return -1
        logging.info(f'Copying {file}: SUCCESS')
        logging.info(f'{fileName}')

    return 0


if __name__ == '__main__':
    git_hub_url = 'https://raw.githubusercontent.com/Bill374/2000-sail-polars/main/'
    directory = os.getcwd()
    logging.basicConfig(level=logging.INFO)
    rc = copy_files(git_hub_url, directory, 'core')
    if not rc:
        logging.info('Python modules successully installed.')
    else:
        logging.error('Error installing python modules.')

