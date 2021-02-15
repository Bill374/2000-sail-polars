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

    logging.info(f'Copying {option} files from {git_hub_url}')
    logging.info(f'Copying {option} files to {install_directory}')

    file_list = files.splitlines(False)
    file_list = list(filter(None, file_list))

    for file in file_list:
        logging.info(f'Copying {file}')
        fileToGet = f'{git_hub_url}{file}'
        try:
            fileName = wget.download(fileToGet, out=install_directory)
        except Exception as http_error:
            logging.error(f'Copying {file}: FAIL')
            logging.error(http_error)
            return -1
        logging.info(f'Copying {file}: SUCCESS')
        logging.info(f'{fileName}')

    return 0


def install_linux_packages():
    """
    Install required linux packages listed in install.cfg.

    apt-get update
    update is used to resynchronize the package index files from their sources.
    The indexes of available packages are fetched from the location(s)
    specified in /etc/apt/sources.list.  An update should always be performed
    before an upgrade.

    apt-get upgrade
    upgrade is used to install the newest versions of all packages currently
    installed on the system from the sources enumerated in
    /etc/apt/sources.list.  Packages currently installed with new versions
    available are retrieved and upgraded; under no circumstances are currently
    installed packages removed, or packages not already installed retrieved
    and installed. New versions of currently installed packages that cannot be
    upgraded without changing the install status of another package will be
    left at their current version.

    apt-get install -y {package}
    Called for each package listed in install.cfg.  -y option forces a yes too
    all prompts during the install process.

    Returns
    -------
    rc : int
         0 : successful
        -1 : error

    """
    config = configparser.ConfigParser(comment_prefixes=(';'))
    config.read('install.cfg')

    try:
        linux_packages = config.get('LINUX', 'packages')
    except configparser.NoSectionError:
        logging.error('LINUX section missing from install.cfg')
        return -1
    except configparser.NoOptionError:
        logging.error('No list of LINUX packages found in install.cfg')
        return -1

    package_list = linux_packages.splitlines(False)
    package_list = list(filter(None, package_list))

    logging.info('Update Linux package index.')
    rc = os.system('apt-get update')
    if not rc:
        logging.info('Update Linux package index: SUCCESS')
    else:
        logging.error('Update Linux index: FAIL')
        return -1

    logging.info('Upgrade existing Linux packages.')
    rc = os.system('apt-get upgrade -y')
    if not rc:
        logging.info('Upgrade existing Linux packages: SUCCESS')
    else:
        logging.error('Upgrade existing Linux packages: FAIL')
        return -1

    for package in package_list:
        logging.info(f'Installing Linux package {package}.')
        rc = os.system(f'apt-get install -y {package}')
        if not rc:
            logging.info(f'Installing Linux package {package}: SUCCESS')
        else:
            logging.error(f'Installing Linux package {package}: FAIL')
            return -1

    return 0


def install_python_modules():
    """
    Install required python modules listed in install.cfg.

    Returns
    -------
    rc : int
         0 : successful
        -1 : error

    """
    config = configparser.ConfigParser(comment_prefixes=(';'))
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

    return 0


def add_lines(section):
    """
    Append lines to the end of a text file.

    The section of install.cfg is expected to contain exactly two options
    file:
        The full path to the file to be edited.
    lines:
        The lines to be appended to the file.

    Each line will only be appended if it is not already found in the file.
    If the file is not found or cannot be opened an error is logged.

    Parameters
    ----------
    section : str
        The section in install.cfg to read.

    Returns
    -------
    rc : int
         0 : successful
        -1 : error

    """
    config = configparser.ConfigParser(comment_prefixes=(';'))
    config.read('install.cfg')

    # Get information from the section of install.cfg
    try:
        file_name = config.get(section, 'file_name')
    except configparser.NoSectionError:
        logging.error(f'{section} not found in install.cfg')
        return -1
    except configparser.NoOptionError:
        logging.error(f'file_name option not found for {section} in '
                      'install.cfg')
        return -1
    try:
        lines = config.get(section, 'lines')
    except configparser.NoOptionError:
        logging.error(f'lines option not found for {section} in install.cfg')
        return -1

    # build a list of dictionaries
    line_list = lines.splitlines(False)
    lines = []
    for x in filter(None, line_list):
        lines.append({"line": x, "found": False})

    # Check if the lines already exist in the file
    logging.info(f'Reading {file_name}, checking if updates required.')
    try:
        file_to_edit = open(file_name, 'r')
    except IOError:
        logging.error(f'Cannot open {file_name} for read')
        return
    for file_line in file_to_edit:
        for i, source in enumerate(lines):
            if file_line.strip('\n') == source["line"]:
                logging.info(f'Found: {source["line"]}')
                lines[i]["found"] = True
    file_to_edit.close()

    # Are there any lines to be added to file_name?
    need_update = False
    for source in lines:
        if not source["found"]:
            need_update = True
    if not need_update:
        logging.info(f'No updates needed to {file_name}')
        return 0

    # Make the required updates to the file
    logging.info(f'Writing to {file_name}')
    try:
        file_to_edit = open(file_name, 'a')
    except IOError:
        logging.error(f'Cannot open {file_name} for write')
        return -1
    file_to_edit.write('\n# RKR Logger\n')
    for source in lines:
        if not source["found"]:
            logging.info(f'Writing: {source["line"]}')
            file_to_edit.write(f'{source["line"]}\n')
    file_to_edit.close()
    logging.info(f'Finished modifying {file_name}')

    return 0


def main(git_hub_url):
    """
    Main installation function.

    Returns
    -------
    None.

    """
    logging.info('*** Start main-install ***')
    directory = os.getcwd()

    logging.info('*** Core Files ***')
    rc = copy_files(git_hub_url, directory, 'core')
    if not rc:
        logging.info('Core files successfully installed.')
    else:
        logging.error('Error installing core files.')
        return rc

    logging.info('*** Linux Packages ***')
    rc = install_linux_packages()
    if not rc:
        logging.info('Linux packages successfully installed.')
    else:
        logging.error('Error installing Linux packages.')
        return rc

    logging.info('*** Python Modules ***')
    rc = install_python_modules()
    if not rc:
        logging.info('Python modules successfully installed.')
    else:
        logging.error('Error installing python modules.')
        return rc

    logging.info('*** Update Files ***')
    sections = ['BOOT-CONFIG']
    for section in sections:
        rc = add_lines(section)
        if not rc:
            logging.info(f'{section} successfully executed.')
        else:
            logging.error(f'Error executing {section}.')
            return rc

    logging.info('*** End main-install ***')
    return 0
