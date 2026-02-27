import numpy as np

from projections import ProjectionConfig, forward_projection, inverse_projection


def _roundtrip(cfg, lon, lat, atol=1e-5):
    x, y, vis = forward_projection(lon, lat, cfg)
    lon2, lat2, vis2 = inverse_projection(x, y, cfg)
    assert np.all(vis)
    assert np.all(vis2)
    dlon = ((lon2 - lon + 180.0) % 360.0) - 180.0
    assert np.allclose(dlon, 0.0, atol=atol)
    assert np.allclose(lat2, lat, atol=atol)


def test_roundtrip_equirectangular():
    cfg = ProjectionConfig(name="equirectangular", center_lon_deg=10, center_lat_deg=-5)
    lon = np.array([-170, -30, 45, 179], dtype=float)
    lat = np.array([-60, -10, 30, 70], dtype=float)
    _roundtrip(cfg, lon, lat)


def test_roundtrip_mercator():
    cfg = ProjectionConfig(name="mercator", center_lon_deg=0, center_lat_deg=0)
    lon = np.array([-170, -30, 45, 179], dtype=float)
    lat = np.array([-70, -10, 30, 70], dtype=float)
    _roundtrip(cfg, lon, lat)


def test_roundtrip_azimuthal_equidistant():
    cfg = ProjectionConfig(name="azimuthal_equidistant", center_lon_deg=20, center_lat_deg=10)
    lon = np.array([10, 20, 60, -120], dtype=float)
    lat = np.array([0, 25, -30, 45], dtype=float)
    _roundtrip(cfg, lon, lat, atol=1e-4)


def test_roundtrip_stereographic():
    cfg = ProjectionConfig(name="stereographic", center_lon_deg=0, center_lat_deg=45, stereographic_max_c_deg=160)
    lon = np.array([0, 20, -30, 80], dtype=float)
    lat = np.array([45, 60, 30, 10], dtype=float)
    _roundtrip(cfg, lon, lat, atol=1e-4)
