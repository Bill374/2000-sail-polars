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


def zip_logs():
    """
    Zip all the log files.

    Zip all the log files to save space and reduce costs for data transmission
    to Google Drive.
    Each log file with the extension .n2k is zipped into a separate archive.
    It is important that this function is not called when logging is in
    progress or bad things could happen.  Perhaps we should give the active
    log file a different extension and only rename it to .n2k after it is
    closed

    Returns
    -------
    None.

    """

    logger = logging.getLogger('rkrutils')

    logger.info('Checking for files ending with .n2k')
    found = 0
    failed = 0
    for file in os.listdir():
        if file.endswith('.n2k'):
            found += 1
            logger.info(f'Found {file}')
            zip_filename = f'{file}.zip'
            try:
                with zipfile.ZipFile(zip_filename, 'w') as log_zip:
                    log_zip.write(file)
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
        logger.info('No files ending with .n2k')
    else:
        logger.info(f'Found {found} files ending with .n2k')
        logger.info(f'Successfully zipped {found - failed} files')
        if failed:
            logger.info(f'Failed to zip {failed} files')
    return None


def send_to_drive():
    """
    Send all log files to Google Drive.

    Send all log files from the Pi to Google Drive.  If the file transfer was
    successful delete the log files from the Pi

    Returns
    -------
    None.

    """

    logger = logging.getLogger('rkrutils')
    logger.info('Zip files before sending to Google Drive')
    zip_logs()

    return None
