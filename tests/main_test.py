"""
main test script
To run issue the command pytest at the root folder of the project.
"""
from pathlib import Path
from unittest.mock import patch

import pytest
import torch
from time_series_predictor import TimeSeriesPredictor

from src.model import BenchmarkLSTM
from src.oze_dataset import OzeNPZDataset, npz_check, utils


def _get_credentials(user_name, user_password):
    credentials = {}
    credentials['user_name'] = user_name
    credentials['user_password'] = user_password
    return credentials

def _get_dataset(user_name, user_password):
    return OzeNPZDataset(
        dataset_path=npz_check(
            Path('datasets'),
            'dataset',
            credentials=_get_credentials(user_name, user_password)
        )
    )

def test_lstm_tsp_fitting_oze(user_name, user_password):
    """
    Tests the LSTMTimeSeriesPredictor
    """
    tsp = TimeSeriesPredictor(
        BenchmarkLSTM(hidden_dim=64),
        max_epochs=5,
        # train_split=None, # default = skorch.dataset.CVSplit(5)
        optimizer=torch.optim.Adam
    )
    dataset = _get_dataset(user_name, user_password)

    tsp.fit(dataset)
    mean_r2_score = tsp.score(tsp.dataset)
    assert mean_r2_score > -300

def test_lstm_tsp_forecast_oze(user_name, user_password):
    """
    Tests the LSTMTimeSeriesPredictor
    """
    tsp = TimeSeriesPredictor(
        BenchmarkLSTM(hidden_dim=64),
        max_epochs=5,
        # train_split=None, # default = skorch.dataset.CVSplit(5)
        optimizer=torch.optim.Adam
    )
    dataset = _get_dataset(user_name, user_password)

    tsp.fit(dataset)
    mean_r2_score = tsp.score(tsp.dataset)
    assert mean_r2_score > -300

    predictions = tsp.forecast(500)
    assert len(predictions) == len(dataset)+500

def test_lstm_tsp_fitting_in_cpu_oze(user_name, user_password):
    """
    Tests the LSTMTimeSeriesPredictor fitting
    """
    tsp = TimeSeriesPredictor(
        BenchmarkLSTM(hidden_dim=64),
        max_epochs=5,
        # train_split=None, # default = skorch.dataset.CVSplit(5)
        optimizer=torch.optim.Adam,
        device='cpu'
    )
    dataset = _get_dataset(user_name, user_password)

    tsp.fit(dataset)
    mean_r2_score = tsp.score(tsp.dataset)
    assert mean_r2_score > -300

@patch.object(utils, '_get_files_to_download')
@patch.object(utils, '_get_local_credentials')
def test_no_credentials(mock_get_local_credentials, mock_get_files_to_download):
    """test_no_credentials
    """
    def patched_get_files_to_download():
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
        files_to_download = [x_train, y_train, x_test]
        make_npz_info = {}
        make_npz_info['flag'] = True
        make_npz_info['args'] = (x_train['filename'], y_train['filename'])
        return files_to_download, make_npz_info
    mock_get_local_credentials.return_value = (None, None)
    mock_get_files_to_download.return_value = patched_get_files_to_download()
    with pytest.raises(ValueError) as error:
        npz_check(
            Path('datasets'),
            'dataset'
        )
    # pylint: disable=line-too-long
    link = 'https://github.com/maxjcohen/ozechallenge_benchmark/blob/master/README.md#download-using-credentials-optional'
    assert error.match(f'Missing login credentials. Make sure you follow {link}')
