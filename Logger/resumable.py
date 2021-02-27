#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 16:52:22 2021

@author: wmorland
"""

import json
import os
import requests
from google.oauth2 import service_account as ggl_acc

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = '/opt/RKR-Logger/Keys/rkr-logger-54e7a45a3091.json'
FOLDER_ID = '13GV4SPZg1tIh-9VJk_6NBqFIUUj2ia6V'

rkr_creds = ggl_acc.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# access_token = '###'  # Please set the access token.

filename = './sample.png'

filesize = os.path.getsize(filename)

# 1. Retrieve session for resumable upload.

headers = {
    'Authorization': f'Bearer {rkr_creds}',
    'Content-Type': 'application/json'
    }

params = {
    'name': filename,
    'mimeType': 'appliacation/octet-stream'
}

r = requests.post(
    "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
    headers=headers,
    data=json.dumps(params)
)
location = r.headers['Location']

# 2. Upload the file.

headers = {'Content-Range': f'bytes 0-{str(filesize - 1)}/{str(filesize)}'}
r = requests.put(location, headers=headers, data=open(filename, 'rb'))

print(r.text)
