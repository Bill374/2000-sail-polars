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
from google.oauth2 import service_account as ggl_acc
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


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


def send_to_drive(directory='.'):
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
    zip_logs(directory)

    SCOPES = ['https://www.googleapis.com/auth/drive']
    # Should read these from the config file or an environment variable
    SERVICE_ACCOUNT_FILE = '/opt/RKR-Logger/Keys/rkr-logger-54e7a45a3091.json'
    FOLDER_ID = '13GV4SPZg1tIh-9VJk_6NBqFIUUj2ia6V'

    rkr_creds = ggl_acc.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    drive_service = build('drive', 'v3', credentials=rkr_creds)

    logger.info('Checking for files ending with .zip')
    found = 0
    failed = 0
    for pi_file in os.listdir(directory):
        if pi_file.endswith('.zip'):
            found += 1
            logger.info(f'Found {pi_file}')

            # mimetype
            # *.n2k text/plain
            # *.n2k.zip application/octet-stream
            # need to pick out just the file name without the directory
            file = pi_file
            file_metadata = {
                'name': file,
                'parents': [FOLDER_ID]
                }
            # This method has a limit of a 5Mb file.
            # We will need a resumable upload.
            media = MediaFileUpload(pi_file,
                                    mimetype='appliacation/octet-stream')
            logger.info(f'Attempting to upload {pi_file} to Google Drive')
            try:
                drive_service.files().create(body=file_metadata,
                                             media_body=media,
                                             fields='id').execute()
                logger.info(f'Uploading {pi_file} to Google Drive: SUCCESS')
                logger.info(f'Removing {pi_file}.')
                os.remove(pi_file)
            except HttpError as http_error:
                failed += 1
                logger.error(f'Uploading {pi_file} to Google Drive: FAIL')
                logger.error(http_error)

    if not found:
        logger.info('No files ending with .zip')
    else:
        logger.info(f'Found {found} files ending with .zip')
        logger.info(f'Successfully uploaded {found - failed} files')
        if failed:
            logger.info(f'Failed to upload {failed} files')

    return None


def send_to_drive_resumable(directory='.'):
    """
    Send all log files to Google Drive.

    Send all log files from the Pi to Google Drive.  If the file transfer was
    successful delete the log files from the Pi.
    This version uses resumable upload that avoids the 5Mb per file limit.

    Returns
    -------
    None.

    """
