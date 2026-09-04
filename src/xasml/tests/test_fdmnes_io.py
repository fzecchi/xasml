import pytest

from xasml.datasets.fdmnes.io import Fdmnes


def test_convolve_rejects_missing_step():
    with pytest.raises(ValueError, match="convolution step"):
        Fdmnes.convolve([], [], [], step=None)
