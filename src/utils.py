"""
Utils
"""
import json
import os
import threading
from os import makedirs, path, remove
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv
import requests
from lxml import html
from tqdm import tqdm
import re

import sys

def download_from_url(session_requests, url, destination_folder):
    """
    @param: url to download file
    @param: dst place to put the file
    """
    result = session_requests.get(
        url,
        stream = True,
        headers = dict(referer = url)
    )
    download_details = {}
    download_details['name'] = re.findall("filename=(.+)", result.headers['content-disposition'])[0]
    download_details['size'] = int(result.headers["Content-Length"])

    dst = os.path.join(destination_folder, download_details['name'])
    if Path(dst).is_file():
        first_byte = os.path.getsize(dst)
    else:
        first_byte = 0
    if first_byte >= download_details['size']:
        return download_details['size']
    header = {"Range": "bytes=%s-%s" % (first_byte, download_details['size'])}
    pbar = tqdm(
        total=download_details['size'],
        initial=first_byte,
        unit='B',
        unit_scale=True,
        desc=download_details['name'])
    req = session_requests.get(url, headers=header, stream=True)
    with(open(dst, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                pbar.update(1024)
    pbar.close()
    return download_details['size']

class DownloadThread(threading.Thread):
    """
    DownloadThread
    """
    def __init__(self, session_requests, url, path):
        threading.Thread.__init__(self)
        self.session_requests = session_requests
        self.url = url
        self.path = path
    def run(self):
        """
        Download a file from given url
        """
        download_from_url(self.session_requests, self.url, self.path)

def npz_check(datasets_path, output_filename):
    """
    make sure npz is present
    """
    output_extension = ".npz"
    dataset_path_str = path.join(datasets_path, output_filename+output_extension)
    x_train = \
        ('https://challengedata.ens.fr/participants/challenges/28/download/x-train',
         'x_train_LsAZgHU.csv')
    y_train = \
        ('https://challengedata.ens.fr/participants/challenges/28/download/y-train',
         'y_train_EFo1WyE.csv')
    x_test = \
        ('https://challengedata.ens.fr/participants/challenges/28/download/x-test',
         'x_test_QK7dVsy.csv')
    make_npz_flag = False
    files_to_download = list()
    if not Path(datasets_path).is_dir():
        # If there is no datasets folder
        makedirs(datasets_path)
        files_to_download = [x_train, y_train, x_test]
        make_npz_flag = True
    else:
        # If there is datasets folder
        if not Path(path.join(datasets_path, x_test[1])).is_file():
            # If there is datasets folder but there isn't x_test file
            files_to_download.append(x_test)
        if not Path(dataset_path_str).is_file():
            # If there is datasets folder but there isn't output npz file
            make_npz_flag = True
            if not Path(path.join(datasets_path, x_train[1])).is_file():
                # If there is datasets folder but there isn't output npz file and there isn't
                # x_train file
                files_to_download.append(x_train)
            if not Path(path.join(datasets_path, y_train[1])).is_file():
                # If there is datasets folder but there isn't output npz file and there isn't
                # y_train file
                files_to_download.append(y_train)

    if files_to_download or make_npz_flag:
        if files_to_download:
            login_url = "https://challengedata.ens.fr/login/"
            session_requests = requests.session()
            result = session_requests.get(login_url)
            tree = html.fromstring(result.text)
            authenticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]
            load_dotenv('.env.test.local')
            payload = {
                "username": os.getenv("CHALLENGE_USER_NAME"), 
                "password": os.getenv("CHALLENGE_USER_PASSWORD"), 
                "csrfmiddlewaretoken": authenticity_token
            }
            result = session_requests.post(
                login_url,
                data = payload,
                headers = dict(referer=login_url)
            )
            assert result.status_code == 200

            threads = []
            for file in files_to_download:
                threads.append(DownloadThread(session_requests, file[0], datasets_path))

            # Start all threads
            for thread in threads:
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

        if make_npz_flag:
            make_npz(datasets_path, output_filename, x_train[1], y_train[1])
    return dataset_path_str

def make_npz(datasets_path, output_filename, x_train_filename, y_train_filename):
    """
    Creates the npz file and deletes the x_train and y_train files
    """
    x_train_path = path.join(datasets_path, x_train_filename)
    y_train_path = path.join(datasets_path, y_train_filename)
    # create npz file
    csv2npz(x_train_path, y_train_path, datasets_path, output_filename)
    # there is no more need to keep x_train and y_train files
    remove(x_train_path)
    remove(y_train_path)

def csv2npz(dataset_x_path, dataset_y_path, output_path, filename, labels_path='labels.json'):
    """Load input dataset from csv and create x_train tensor."""
    # Load dataset as csv
    x = pd.read_csv(dataset_x_path)
    y = pd.read_csv(dataset_y_path)

    # Load labels, file can be found in challenge description
    with open(labels_path, "r") as stream_json:
        labels = json.load(stream_json)

    m = x.shape[0]
    K = 672  # Can be found through csv

    # Create R and Z
    R = x[labels["R"]].values
    R = R.astype(np.float32)

    X = y[[f"{var_name}_{i}" for var_name in labels["X"]
           for i in range(K)]]
    X = X.values.reshape((m, -1, K))
    X = X.astype(np.float32)

    Z = x[[f"{var_name}_{i}" for var_name in labels["Z"]
           for i in range(K)]]
    Z = Z.values.reshape((m, -1, K))
#     Z = Z.transpose((0, 2, 1))
    Z = Z.astype(np.float32)

    np.savez(path.join(output_path, filename), R=R, X=X, Z=Z)
