"""
transformer_tsp
"""
import torch
from tst import Transformer

from .time_series_predictor import TimeSeriesPredictor  # pylint: disable=relative-beyond-top-level


class TransformerTimeSeriesPredictor(TimeSeriesPredictor):
    """
    TransformerTimeSeriesPredictor
    """

    def __init__(self,
                 learning_rate=2e-4,
                 epochs=30,
                 d_model=64,
                 query_size=8,
                 value_size=8,
                 number_of_heads=8,
                 number_of_coders=4,
                 attention_size=12,
                 dropout=0.2,
                 positional_encoding=None,
                 chunk_mode=None):
        super().__init__(learning_rate, epochs)
        self.d_model = d_model
        # Model parameters
        self.query_size = query_size  # Query size
        self.value_size = value_size  # Value size
        self.number_of_heads = number_of_heads  # Number of heads
        self.number_of_coders = number_of_coders  # Number of encoder and decoder to stack
        self.attention_size = attention_size  # Attention window size
        self.dropout = dropout  # Dropout rate
        self.positional_encoding = positional_encoding  # Positional encoding
        self.chunk_mode = chunk_mode

    def fit(self, dataset, loss_function=torch.nn.MSELoss()):
        """
        Fit transformer network
        """
        d_input = dataset.get_x_shape()[2]     # From dataset
        d_output = dataset.get_y_shape()[2]    # From dataset
        net = Transformer(d_input, self.d_model, d_output, self.query_size, self.value_size, self.number_of_heads, self.number_of_coders,
                          attention_size=self.attention_size, dropout=self.dropout, chunk_mode=self.chunk_mode, pe=self.positional_encoding)
        return super().fit(dataset, net, loss_function=loss_function)

    def make_future_dataframe(self):
        """
        Make future dataframe
        """
        pass
