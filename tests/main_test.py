"""
main test script
To run issue the command pytest at the root folder of the project.
"""
from pathlib import Path
from time_series_predictor import TimeSeriesPredictor
import torch

from src.model import BenchmarkLSTM
from src.oze_dataset import OzeNPZDataset, npz_check

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
        BenchmarkLSTM(),
        max_epochs=5,
        # train_split=None, # default = skorch.dataset.CVSplit(5)
        optimizer=torch.optim.Adam
    )
    dataset = _get_dataset(user_name, user_password)

    tsp.fit(dataset)
    mean_r2_score = tsp.score(tsp.dataset)
    assert mean_r2_score > -200

def test_lstm_tsp_fitting_in_cpu_oze(user_name, user_password):
    """
    Tests the LSTMTimeSeriesPredictor fitting
    """
    tsp = TimeSeriesPredictor(
        BenchmarkLSTM(),
        max_epochs=5,
        # train_split=None, # default = skorch.dataset.CVSplit(5)
        optimizer=torch.optim.Adam,
        device='cpu'
    )
    dataset = _get_dataset(user_name, user_password)

    tsp.fit(dataset)
    mean_r2_score = tsp.score(tsp.dataset)
    assert mean_r2_score > -200
