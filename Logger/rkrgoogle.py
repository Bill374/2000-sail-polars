#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 15:57:52 2021

@author: wmorland
"""

import os
import logging
from google.oauth2 import service_account as ggl_acc
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from rkrutils import zip_logs


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
    return None
