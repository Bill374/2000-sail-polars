#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 18:37:20 2021

@author: wmorland
"""

import os
import logging
import zipfile
import contextlib
from pathlib import Path
import shutil


def zip_logs(directory='.', file_extension='.n2k'):
    """
    Zip all the log files.

    Zip all the log files to save space and reduce costs for data transmission
    to Google Drive.  Interestingly this may not actually save space.  Early
    tests show that the zipped files are not much smaller.
    Each log file that matches file_extension is zipped into a separate
    archive.  It is important that this function is not called when logging is
    in progress or bad things could happen.  Perhaps we should give the active
    log file a different extension and only rename it to .n2k after it is
    closed.

    Parameters
    ----------
    directory : str
        The directory to search for log files to zip.  Defaults to the current
        working directory.

    file_extension : str
        The pattern to match for files to zip.  Defaults to .n2k.

    Returns
    -------
    None.

    """

    logger = logging.getLogger('rkrutils')

    logger.info(f'Checking for files ending with {file_extension} in '
                '{directory}')
    found = 0
    failed = 0
    for file in os.listdir(directory):
        if file.endswith(file_extension):
            found += 1
            logger.info(f'Found {file}')
            zip_filename = f'{file}.zip'
            try:
                with zipfile.ZipFile(f'{directory}/{zip_filename}',
                                     'w') as log_zip:
                    log_zip.write(f'{directory}/{file}')
                    if log_zip.testzip() is not None:
                        failed += 1
                        logger.error(f'Zipping {file} into {zip_filename}: '
                                     'FAIL')
                        with contextlib.suppress(FileNotFoundError):
                            os.remove(zip_filename)
                    else:
                        logger.info(f'Zipping {file} into {zip_filename}: '
                                    'SUCCESS')
                        logger.info(f'Removing {file}.')
                        os.remove(file)
            except zipfile.BadZipFile:
                failed += 1
                logger.error(f'Zipping {file} into {zip_filename}: FAIL')

    if not found:
        logger.info(f'No files ending with {file_extension}')
    else:
        logger.info(f'Found {found} files ending with {file_extension}')
        logger.info(f'Successfully zipped {found - failed} files')
        if failed:
            logger.info(f'Failed to zip {failed} files')
    return None


def send_to_usb(pi_directory='.', file_extension='.n2k'):
    """
    Copy files to removable USB storage.

    All files from the pi directory matching the file_extension are copied to
    the USB storage.  If the copy is successful the files are deleted from the
    Pi.
    The USB drive is expected to be mounted at the location specified in the
    environment variable USBDRIVE.  If the drive is not mounted an error is
    logged.

    Parameters
    ----------
    pi_directory : str, optional
        Source directory for files. The default is '.'.
    file_extension : str, optional
        File extension to match. The default is '.n2k'.

    Returns
    -------
    None.

    """
    logger = logging.getLogger('rkrutils')

    usb_directory = os.getenv('USBDRIVE')
    logger.info(f'Looking for USB drive at {usb_directory}')
    if not os.path.ismount(usb_directory):
        logger.warning(f'USB drive not mounted at {usb_directory}')
        # maybe we can try to mount it
        return None

    found = 0
    failed = 0
    logger.info('Looking for files to copy')
    for pi_file in os.listdir(pi_directory):
        if pi_file.endswith(file_extension):
            found += 1
            logger.info(f'Moving {pi_file} to USB')
            try:
                shutil.move(f'{pi_directory}/{pi_file}',
                            f'{usb_directory}/{pi_file}')
                logger.info(f'Moving {pi_file} to USB: SUCCESS')
            except OSError:
                failed += 1
                logger.warning(f'Moving {pi_file} to USB: FAIL')

    if not found:
        logger.info(f'No files ending with {file_extension}')
    else:
        logger.info(f'Found {found} files ending with {file_extension}')
        logger.info(f'Successfully moved {found - failed} files')
        if failed:
            logger.info(f'Failed to move {failed} files')

    return None
