#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 16:52:22 2021

@author: wmorland
"""

import json
import os
import requests

access_token = '###'  ## Please set the access token.

filename = './sample.png'

filesize = os.path.getsize(filename)

# 1. Retrieve session for resumable upload.

headers = {"Authorization": "Bearer "+access_token, "Content-Type": "application/json"}
params = {
    "name": "sample.png",
    "mimeType": "image/png"
}
r = requests.post(
    "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
    headers=headers,
    data=json.dumps(params)
)
location = r.headers['Location']

# 2. Upload the file.

headers = {"Content-Range": "bytes 0-" + str(filesize - 1) + "/" + str(filesize)}
r = requests.put(
    location,
    headers=headers,
    data=open(filename, 'rb')
)
print(r.text)