"""
main test script
To run issue the command pytest at the root folder of the project.
"""
from pathlib import Path
from time_series_predictor import TimeSeriesPredictor
import torch

from src.model import BenchmarkLSTM
from src.oze_dataset import OzeNPZDataset, npz_check

def test_lstm_tsp_fitting_oze():
    """
    Tests the LSTMTimeSeriesPredictor
    """
    tsp = TimeSeriesPredictor(
        BenchmarkLSTM(),
        max_epochs=5,
        # train_split=None, # default = skorch.dataset.CVSplit(5)
        optimizer=torch.optim.Adam
    )
    dataset = OzeNPZDataset(
        dataset_path=npz_check(
            Path('datasets'),
            'dataset'
        )
    )

    tsp.fit(dataset)
    mean_r2_score = tsp.score(tsp.dataset)
    assert mean_r2_score > -50

def test_lstm_tsp_fitting_in_cpu_oze():
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
    dataset = OzeNPZDataset(
        dataset_path=npz_check(
            Path('datasets'),
            'dataset'
        )
    )

    tsp.fit(dataset)
    mean_r2_score = tsp.score(tsp.dataset)
    assert mean_r2_score > -50
