# coding: UTF-8
"""This module defines an example Torch network.

Example
-------
$ net = BenchmarkLSTM()

"""

import torch.nn as nn


class BenchmarkLSTM(nn.Module):
    """Example network for solving Oze datachallenge.

    Attributes
    ----------
    lstm: Torch LSTM
        LSTM layers.
    linear: Torch Linear
        Fully connected layer.
    """

    def __init__(self, input_dim=1, hidden_dim=64, output_dim=1, num_layers=3, **kwargs):
        """Defines LSTM and Linear layers.

        Parameters
        ----------
        input_dim: int, optional
            Input dimension. Default is 1. Will be set dinamically based on the data
        hidden_dim: int, optional
            Latent dimension. Default is 100.
        output_dim: int, optional
            Output dimension. Default is 1. Will be set dinamically based on the data
        num_layers: int, optional
            Number of LSTM layers. Default is 3.
        """
        super().__init__(**kwargs)

        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_dim, output_dim)

    # pylint: disable=arguments-differ
    def forward(self, x):
        """Propagate input through the network.

        Parameters
        ----------
        x: Tensor
            Input tensor with shape (m, K, input_dim)

        Returns
        -------
        output: Tensor
            Output tensor with shape (m, K, output_dim)
        """
        lstm_out, _ = self.lstm(x)
        output = self.linear(lstm_out)
        return output
