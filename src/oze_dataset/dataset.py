"""This module defines an example Torch dataset from the Oze datachallenge.

Example
-------
$ dataloader = DataLoader(OzeDataset(DATSET_PATH),
                          batch_size=BATCH_SIZE,
                          shuffle=True,
                          num_workers=NUM_WORKERS)

"""

import os
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from time_series_predictor import TimeSeriesDataset

TIME_SERIES_LENGTH = 672

class OzeEvaluationDataset(Dataset):
    """Torch dataset for Oze datachallenge evaluation.

    Load dataset from two train.csv and test.csv file.

    Attributes
    ----------
    x: np.array
        Dataset input of shape (m, K, 37).
    labels: Dict
        Ordered labels list for R, Z and X.
    m: np.array
        Normalization constant.
    M: np.array
        Normalization constant.
    """

    def __init__(
            self,
            dataset_x_path,
            time_series_length=TIME_SERIES_LENGTH,
            labels_path="labels.json",
            **kwargs):
        """Load dataset from csv.

        Parameters
        ---------
        dataset_x_path: str or Path
            Path to the dataset inputs as csv.
        labels_path: str or Path, optional
            Path to the labels, divided in R, Z and X, in json format.
            Default is "labels.json".
        """
        super().__init__(**kwargs)

        self._load_x_from_csv(dataset_x_path, time_series_length, labels_path)

    # pylint: disable=invalid-name
    def _load_x_from_csv(self, dataset_x_path, time_series_length, labels_path):
        """Load input dataset from csv and create x_train tensor."""
        # Load dataset as csv
        x = pd.read_csv(dataset_x_path)

        # Load labels, file can be found in challenge description
        with open(labels_path, "r") as stream_json:
            self.labels = json.load(stream_json)

        m = x.shape[0]
        K = time_series_length

        # Create R and Z
        R = x[self.labels["R"]].values
        R = np.tile(R[:, np.newaxis, :], (1, K, 1))
        R = R.astype(np.float32)

        Z = x[[f"{var_name}_{i}" for var_name in self.labels["Z"]
               for i in range(K)]]
        Z = Z.values.reshape((m, -1, K))
        Z = Z.transpose((0, 2, 1))
        Z = Z.astype(np.float32)

        # Store R and Z as x_train
        self.x = np.concatenate([Z, R], axis=-1)
        # Normalize
        self.M = np.max(self.x, axis=(0, 1))
        self.m = np.min(self.x, axis=(0, 1))
        self.x = (self.x - self.m) / (self.M - self.m + np.finfo(float).eps)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        return self.x[idx]

    def __len__(self):
        return self.x.shape[0]

    def get_x_shape(self):
        return self.x.shape

class OzeNPZDataset(TimeSeriesDataset):
    """Torch dataset for Oze datachallenge evaluation.

    Load dataset from a single npz file.

    Attributes
    ----------
    x: np.array
        Dataset input of shape (m, K, 37).
    y: np.array
        Dataset target of shape (m, K, 8).
    labels: Dict
        Ordered labels list for R, Z and X.
    m: np.array
        Normalization constant.
    M: np.array
        Normalization constant.
    """

    # pylint: disable=invalid-name
    def __init__(self,
                 dataset_path,
                 labels_path=Path(__file__).parent.joinpath('labels.json')):
        """Load dataset from npz.

        Parameters
        ---------
        dataset_x: str or Path
            Path to the dataset inputs as npz.
        labels_path: str or Path, optional
            Path to the labels, divided in R, Z and X, in json format.
            Default is "labels.json".
        """
        def load_npz(dataset_path, labels_path):
            """Load dataset from csv and create x_train and y_train tensors."""
            def make_predictor(features):
                #pylint: disable=too-many-function-args
                return np.concatenate(features, axis=-1).astype(np.float32)
            # Load dataset as csv
            dataset = np.load(dataset_path)

            # Load labels, can be found through csv or challenge description
            with open(labels_path, "r") as stream_json:
                labels = json.load(stream_json)

            R, X, Z = dataset['R'], dataset['X'], dataset['Z']
            K = Z.shape[-1]  # Time serie length

            R = np.tile(R[:, np.newaxis, :], (1, K, 1))
            Z = Z.transpose((0, 2, 1))
            X = X.transpose((0, 2, 1))

            # Store input features
            input_features = [Z, R]
            x = make_predictor(input_features)

            # Store output features
            output_features = [X]
            y = make_predictor(output_features)

            return (x, y, labels)
        x, y, labels = load_npz(dataset_path, labels_path)
        super().__init__(x, y, labels)

    # pylint: disable=arguments-differ
    def make_future_dataframe(self, *args, include_history=True, **kwargs):
        parent_path = Path(__file__).parent
        dataset_eval = OzeEvaluationDataset(
            parent_path.joinpath(
                os.path.join('..', '..', 'datasets', 'x_test_QK7dVsy.csv')
            ),
            TIME_SERIES_LENGTH, labels_path=parent_path.joinpath('labels.json'))
        if include_history:
            return np.concatenate([self.x, dataset_eval.x])
        return dataset_eval.x
