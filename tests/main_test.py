"""
main test script
To run issue the command pytest at the root folder of the project.
"""
from pathlib import Path
from os import makedirs, rmdir, rename
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
    assert mean_r2_score > -300

def test_lstm_tsp_forecast_oze(user_name, user_password):
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
    assert mean_r2_score > -300

    predictions = tsp.forecast(500)
    assert len(predictions) == len(dataset)+500

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
    assert mean_r2_score > -300

def test_no_credentials():
    """
    Tests the LSTMTimeSeriesPredictor fitting
    """
    dummy_datasets_path = Path('dummy')
    makedirs(dummy_datasets_path)
    oze_path = Path('src').joinpath('oze_dataset')
    env_path1 = oze_path.joinpath('.env.test.local')
    env_path2 = oze_path.joinpath('.env.test.loca1')
    if env_path1.is_file:
        rename(env_path1, env_path2)
    try:
        npz_check(
            dummy_datasets_path,
            'dataset'
        )
        raise Exception("Should have raised an exception!")
    # pylint: disable=broad-except
    except Exception as exception:
        assert type(exception).__name__ == 'ValueError'
        # pylint: disable=line-too-long
        link = 'https://github.com/maxjcohen/ozechallenge_benchmark/blob/master/README.md#download-using-credentials-optional'
        assert str(exception) == f'Missing login credentials. Make sure you follow {link}'
    rmdir(dummy_datasets_path)
    if env_path2.is_file:
        rename(env_path2, env_path1)
