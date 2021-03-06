#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 21:24:52 2021

@author: wmorland
"""

import logging
import os
import wget
import configparser
import stat
import shutil
import subprocess


def make_directory(directory, pi_owner=False):
    """
    If directory does not already exist create it.

    Parameters
    ----------
    directory : string
        directory to be created.
    pi_owner : boolean
        True if the directory needs to be owned by the pi user

    Returns
    -------
    rc : int
         0 : successful
        -1 : error

    """
    # Check that the install directory exists and is a directory.
    logging.info(f'Checking for {directory}')
    if not os.path.isdir(directory):
        logging.info(f'{directory} does not exist.')
        try:
            os.makedirs(directory)
            logging.info(f'makedirs({directory}): SUCCESS')
        except OSError:
            logging.error(f'makedirs({directory}): FAIL')
            return -1
        logging.info(f'{directory} OK.')
    if pi_owner:
        shutil.chown(directory, 'pi', 'pi')
        logging.info(f'{directory} owned by pi user')

    return 0


def create_directories():
    """
    Create each directory in install.cfg if it does not already exist.

    Directory list is read from [DIRECTORY] section of install.cfg.
    Each directory is chown to the pi user.

    Returns
    -------
    rc : int
         0 : successful
        -1 : error

    """
    config = configparser.ConfigParser()
    config.read('install.cfg')

    # List of directories to create
    try:
        logging.info('Reading [DIRECTORY], list from install.cfg')
        directories = config.get('DIRECTORY', 'list')
    except configparser.NoSectionError:
        logging.error('DIRECTORY section missing from install.cfg')
        return -1
    except configparser.NoOptionError:
        logging.error('No list of directories found in install.cfg')
        return -1

    logging.info('Making directories')
    directory_list = directories.splitlines(False)
    directory_list = list(filter(None, directory_list))
    for directory in directory_list:
        rc = make_directory(directory, pi_owner=True)
        if rc:
            logging.info('Make directory: FAIL')
            return -1

    return 0


def copy_files(option):
    """
    Copy files from GitHub to the Pi.

    The list of files to be installed is read from option in the [FILES]
    section of install.cfg.  Each file is expected to be on a separate line.
    The first line is expected to give the target directory to copy the files
    to.

    If a target file already exists in the target directory on the pi it is
    deleted and replaced with the version from GitHub.

    When option is 'executable' the target files are made execuable by user,
    group and world.

    Parameters
    ----------
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

    # List of files to copy
    try:
        logging.info(f'Reading [FILES], {option} from install.cfg')
        files = config.get('FILES', option)
    except configparser.NoSectionError:
        logging.error('FILES section missing from install.cfg')
        return -1
    except configparser.NoOptionError:
        logging.error(f'No list of {option} files found in install.cfg')
        return -1

    # GitHub location
    try:
        logging.info('Reading [GIT-HUB], git hub URL from install.cfg')
        git_hub_url = config.get('GIT-HUB', 'url')
    except configparser.NoSectionError:
        logging.error('GIT-HUB section missing from install.cfg')
        return -1
    except configparser.NoOptionError:
        logging.error('No url found in install.cfg')
        return -1

    file_list = files.splitlines(False)
    file_list = list(filter(None, file_list))

    # Install directory
    install_directory = file_list.pop(0)

    # Check that the install directory exists and is a directory.
    rc = make_directory(install_directory)
    if rc != 0:
        return -1

    logging.info(f'Copying {option} files from {git_hub_url}')
    logging.info(f'Copying {option} files to {install_directory}')
    if option == 'executable':
        executable = True
    else:
        executable = False

    # copy each file
    for file in file_list:
        logging.info(f'Copying {file}')
        fileToGet = f'{git_hub_url}{file}'
        name_only = file.split('/')[-1]
        target_file = f'{install_directory}/{name_only}'
        if os.path.exists(target_file):
            logging.info(f'{name_only} already exists in {install_directory}. '
                         'Deleting.')
            os.remove(target_file)
        try:
            fileName = wget.download(fileToGet, out=install_directory)
            print('')
        except Exception as http_error:
            logging.error(f'Copying {file}: FAIL')
            logging.error(http_error)
            return -1
        if executable:
            logging.info(f'Make {name_only} executable by all.')
            st = os.stat(target_file)
            os.chmod(target_file,
                     st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

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
    try:
        subprocess.run(['apt-get', '-qy', 'update'], check=True)
    except subprocess.CalledProcessError as process_error:
        rc = process_error.returncode
        logging.error(f'Update Linux index return code = {rc}: FAIL')
        return -1
    logging.info('Update Linux package index: SUCCESS')

    logging.info('Upgrade existing Linux packages.')
    try:
        subprocess.run(['apt-get', '-qy', 'upgrade'], check=True)
    except subprocess.CalledProcessError as process_error:
        rc = process_error.returncode
        logging.error(f'Upgrade existing Linux packages return code = {rc}: '
                      'FAIL')
        return -1
    logging.info('Upgrade existing Linux packages: SUCCESS')

    for package in package_list:
        logging.info(f'Installing Linux package {package}.')
        try:
            subprocess.run(['apt-get', '-qy', 'install', package],
                           check=True)
        except subprocess.CalledProcessError as process_error:
            rc = process_error.returncode
            logging.error(f'Installing Linux package {package} return code '
                          f'= {rc}: FAIL')
            return -1
        logging.info(f'Installing Linux package {package}: SUCCESS')

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
        logging.info(f'Installing Python module {module}')
        try:
            subprocess.run(['pip3', 'install', '--upgrade', module],
                           check=True)
        except subprocess.CalledProcessError as process_error:
            rc = process_error.returncode
            logging.error(f'Installing Python module {module} return code '
                          f'= {rc}: FAIL')
            return -1
        logging.info(f'Installing Python module {module}: SUCCESS')

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

    logging.info(f'Building a list of lines to be added to {file_name}')
    line_list = lines.splitlines(False)
    lines = []
    for x in filter(None, line_list):
        lines.append({"line": x, "found": False})

    # If the file does not exist, create it
    if not os.path.isfile(file_name):
        logging.info(f'{file_name} does not exist.')
        base_directory = os.path.dirname(file_name)
        if not os.path.exists(base_directory):
            logging.info(f'{base_directory} does not exist.')
            logging.ifno(f'Createing {base_directory}')
            os.makedirs(base_directory)
        logging.info(f'Creating {file_name}')
        open(file_name, 'a').close()

    # Check if the lines already exist in the file
    logging.info(f'Reading {file_name}, checking if updates required.')
    try:
        file_to_edit = open(file_name, 'r')
    except IOError:
        logging.error(f'Cannot open {file_name} for read')
        return -1
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


def main():
    """
    Main installation function.

    Returns
    -------
    None.

    """
    logging.info('*** Start pi-install ***')

    # Check a few things before we start.
    if not os.path.isfile('install.cfg'):
        logging.error('install.cfg not found in the current directory.')
        return -1
    logging.info('Found install.cfg')

    # Check that the is the most up-to-date version of this script
    # How best to do that?

    logging.info('*** Directories ***')
    rc = create_directories()
    if rc:
        logging.error('Directories: FAIL')
        return rc
    logging.info('Directories: SUCCESS')

    logging.info('*** Copy Files ***')
    files_options = ['core', 'test', 'executable']
    for option in files_options:
        logging.info(f'Copy {option} files')
        rc = copy_files(option)
        if rc:
            logging.error(f'Copy {option} files: FAIL')
            return rc
        logging.info(f'Copy {option} files: SUCCESS')
    logging.info('Copy Files: SUCCESS')

    logging.info('*** Linux Packages ***')
    rc = install_linux_packages()
    if rc:
        logging.error('Linux Packages: FAIL')
        return rc
    logging.info('Linux Packages: SUCCESS')

    logging.info('*** Python Modules ***')
    rc = install_python_modules()
    if rc:
        logging.error('Python Modules: FAIL')
        return rc
    logging.info('Python Modules: SUCCESS')

    logging.info('*** Update System Files ***')
    sections = ['BOOT-CONFIG', 'ENVIRONMENT', 'CRONTAB', 'FSTAB']
    for section in sections:
        logging.info(f'Executing {section}')
        rc = add_lines(section)
        if rc:
            logging.error(f'{section} executed: FAIL')
            return rc
        logging.info(f'{section} executed: SUCCESS')
    logging.info('Update System Files: SUCCESS')

    logging.info('*** End pi-install ***')
    return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        handlers=[
                            logging.FileHandler('pi_install.log'),
                            logging.StreamHandler()
                            ])
    logging.shutdown()
    main()
