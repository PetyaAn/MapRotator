import numpy as np

from render import _bilinear_sample_wrap_x


def test_bilinear_wraps_antimeridian():
    # 1x4 image with distinct columns
    src = np.array([[[0, 0, 0, 255], [10, 0, 0, 255], [20, 0, 0, 255], [30, 0, 0, 255]]], dtype=np.float32)
    # sample near last pixel and beyond edge should blend with first pixel
    sx = np.array([[3.75]], dtype=np.float32)
    sy = np.array([[0.0]], dtype=np.float32)
    out = _bilinear_sample_wrap_x(src, sx, sy)
    # 75% between 30 and 0 due wrap => 7.5
    assert np.allclose(out[0, 0, 0], 7.5, atol=1e-5)
