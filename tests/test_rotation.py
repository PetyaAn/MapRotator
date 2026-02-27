import numpy as np

from rotation import rotate_lonlat


def test_rotation_about_north_pole_90deg():
    lon, lat = rotate_lonlat(np.array([0.0]), np.array([0.0]), 0.0, 90.0, 90.0)
    assert np.allclose(lat, 0.0, atol=1e-6)
    assert np.allclose(lon, 90.0, atol=1e-6)


def test_axis_point_stays_fixed():
    lon0 = np.array([45.0])
    lat0 = np.array([20.0])
    lon, lat = rotate_lonlat(lon0, lat0, 45.0, 20.0, 123.0)
    assert np.allclose(lon, lon0, atol=1e-6)
    assert np.allclose(lat, lat0, atol=1e-6)
