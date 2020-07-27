"""
Utils
"""
import json
import os
import re
import threading
import cgi
from os import makedirs, path, remove

from pathlib import Path
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

from dotenv import load_dotenv
from lxml import html

from .dataset import TIME_SERIES_LENGTH

def download_from_url(session_requests, url, destination_folder):
    """
    @param: url to download file
    @param: dst place to put the file
    """
    response = session_requests.get(
        url,
        stream=True,
        headers=dict(referer=url)
    )
    assert response.ok

    download_details = {}
    if 'Content-Disposition' in response.headers:
        value, params = cgi.parse_header(response.headers['Content-Disposition'])
        if not (value == 'attachment' and 'filename' in params):
            raise ValueError('Cannot retrieve filename')
        download_details['name'] = params['filename']
        download_details['size'] = int(response.headers["Content-Length"])
    else:
        raise ValueError('Cannot retrieve Content-Disposition')

    dst = destination_folder.joinpath(download_details['name'])
    if dst.is_file():
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
    response = session_requests.get(url, headers=header, stream=True)
    assert response.ok

    with(open(dst, 'ab')) as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
                pbar.update(1024)
    pbar.close()
    return download_details['size']


class DownloadThread(threading.Thread):
    """
    DownloadThread
    """

    def __init__(self, session_requests, url, given_path):
        threading.Thread.__init__(self)
        self.session_requests = session_requests
        self.url = url
        self.path = given_path

    def run(self):
        """
        Download a file from given url
        """
        download_from_url(self.session_requests, self.url, self.path)

def _get_files_to_download(datasets_path, dataset_path):
    x_train = {
        'url': 'https://challengedata.ens.fr/participants/challenges/28/download/x-train',
        'filename': 'x_train_LsAZgHU.csv'
    }
    y_train = {
        'url': 'https://challengedata.ens.fr/participants/challenges/28/download/y-train',
        'filename': 'y_train_EFo1WyE.csv'
    }
    x_test = {
        'url': 'https://challengedata.ens.fr/participants/challenges/28/download/x-test',
        'filename': 'x_test_QK7dVsy.csv'
    }
    make_npz_flag = False
    files_to_download = list()
    if not datasets_path.is_dir():
        # If there is no datasets folder
        makedirs(datasets_path)
        files_to_download = [x_train, y_train, x_test]
        make_npz_flag = True
    else:
        # If there is datasets folder
        if not datasets_path.joinpath(x_test['filename']).is_file():
            # If there is datasets folder but there isn't x_test file
            files_to_download.append(x_test)
        if not dataset_path.is_file():
            # If there is datasets folder but there isn't output npz file
            make_npz_flag = True
            if not datasets_path.joinpath(x_train['filename']).is_file():
                # If there is datasets folder but there isn't output npz file and there isn't
                # x_train file
                files_to_download.append(x_train)
            if not datasets_path.joinpath(y_train['filename']).is_file():
                # If there is datasets folder but there isn't output npz file and there isn't
                # y_train file
                files_to_download.append(y_train)
    make_npz_info = {}
    make_npz_info['flag'] = make_npz_flag
    make_npz_info['args'] = (x_train['filename'], y_train['filename'])
    return files_to_download, make_npz_info

def _get_local_credentials():
    load_dotenv(Path(__file__).parent.joinpath('.env.test.local'))
    challenge_user_name = os.getenv("CHALLENGE_USER_NAME")
    challenge_user_password = os.getenv("CHALLENGE_USER_PASSWORD")
    return (challenge_user_name, challenge_user_password)

# pylint: disable=too-many-locals
def npz_check(datasets_path, output_filename, credentials=None):
    """
    make sure npz is present
    """
    def download_files(files_to_download):
        def login_to_challengedata_website(credentials):
            def get_credentials(credentials):
                if credentials is None:
                    challenge_user_name, challenge_user_password = _get_local_credentials()
                    if None in [challenge_user_name, challenge_user_password]:
                        # pylint: disable=line-too-long
                        link = 'https://github.com/maxjcohen/ozechallenge_benchmark/blob/master/README.md#download-using-credentials-optional'
                        raise ValueError(
                            f'Missing login credentials. Make sure you follow {link}')
                else:
                    challenge_user_name = credentials['user_name']
                    challenge_user_password = credentials['user_password']
                return challenge_user_name, challenge_user_password
            login_url = "https://challengedata.ens.fr/login/"
            session_requests = requests.session()
            response = session_requests.get(login_url)
            assert response.ok

            authenticity_token = list(set(html.fromstring(response.text).xpath(
                "//input[@name='csrfmiddlewaretoken']/@value")))[0]
            challenge_user_name, challenge_user_password = get_credentials(credentials)

            response = session_requests.post(
                login_url,
                data={
                    "username": challenge_user_name,
                    "password": challenge_user_password,
                    "csrfmiddlewaretoken": authenticity_token
                },
                headers=dict(referer=login_url)
            )
            assert response.ok
            return session_requests
        session_requests = login_to_challengedata_website(credentials)

        threads = []
        for file in files_to_download:
            threads.append(DownloadThread(
                session_requests, file['url'], datasets_path))

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

    dataset_path = datasets_path.joinpath(output_filename+".npz")
    files_to_download, make_npz_info = _get_files_to_download(datasets_path, dataset_path)

    if files_to_download:
        download_files(files_to_download)

    if make_npz_info['flag']:
        make_npz(datasets_path, output_filename, *make_npz_info['args'])
    return dataset_path

def make_npz(datasets_path, output_filename, x_train_filename, y_train_filename):
    """
    Creates the npz file and deletes the x_train and y_train files
    """
    x_train_path = datasets_path.joinpath(x_train_filename)
    y_train_path = datasets_path.joinpath(y_train_filename)
    print('Creating %s.npz...' % output_filename, end='\r')
    csv2npz(x_train_path, y_train_path, datasets_path, output_filename)
    clear_line_str = '\033[K'
    print(clear_line_str+'Create '+output_filename+'.npz\tDone')
    # there is no more need to keep x_train and y_train files
    remove(x_train_path)
    remove(y_train_path)

# pylint: disable=invalid-name
def csv2npz(dataset_x_path,
            dataset_y_path,
            output_path,
            filename,
            labels_path=Path(__file__).parent.joinpath('labels.json')):
    """Load input dataset from csv and create x_train tensor."""
    # Load dataset as csv
    x = pd.read_csv(dataset_x_path)
    y = pd.read_csv(dataset_y_path)

    # Load labels, file can be found in challenge description
    with open(labels_path, "r") as stream_json:
        labels = json.load(stream_json)

    m = x.shape[0]
    K = TIME_SERIES_LENGTH  # Can be found through csv

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
