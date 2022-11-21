"""
The Python API for equistore also provides functions which operate on
:py:class:`equistore.TensorMap`, and can be used to build Machine Learning
models.

These functions can handle data stored either in numpy arrays or Torch tensor,
and automatically dispatch to the right function for a given TensorMap.
"""

from .allclose import (  # noqa
    allclose,
    allclose_block,
    allclose_block_raise,
    allclose_raise,
)
from .dot import dot  # noqa
from .lstsq import lstsq  # noqa
from .remove_gradients import remove_gradients  # noqa
from .solve import solve  # noqa

__all__ = [
    "allclose",
    "allclose_raise",
    "allclose_block",
    "allclose_block_raise",
    "dot",
    "lstsq",
    "remove_gradients",
    "solve",
]