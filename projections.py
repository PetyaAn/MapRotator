"""Forward and inverse map projections."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


DEG2RAD = np.pi / 180.0
RAD2DEG = 180.0 / np.pi


def wrap_lon_rad(lon: np.ndarray) -> np.ndarray:
    return ((lon + np.pi) % (2 * np.pi)) - np.pi


@dataclass
class ProjectionConfig:
    name: str
    center_lon_deg: float = 0.0
    center_lat_deg: float = 0.0
    mercator_lat_limit_deg: float = 85.0
    stereographic_max_c_deg: float = 170.0

    @property
    def center_lon(self) -> float:
        return self.center_lon_deg * DEG2RAD

    @property
    def center_lat(self) -> float:
        return self.center_lat_deg * DEG2RAD


def projected_bounds(cfg: ProjectionConfig) -> tuple[float, float, float, float]:
    if cfg.name == "equirectangular":
        return -np.pi, np.pi, -np.pi / 2, np.pi / 2
    if cfg.name == "mercator":
        lat_lim = np.deg2rad(cfg.mercator_lat_limit_deg)
        y_max = np.log(np.tan(np.pi / 4 + lat_lim / 2))
        return -np.pi, np.pi, -y_max, y_max
    if cfg.name == "azimuthal_equidistant":
        return -np.pi, np.pi, -np.pi, np.pi
    if cfg.name == "stereographic":
        cmax = np.deg2rad(cfg.stereographic_max_c_deg)
        rho_max = 2 * np.tan(cmax / 2)
        return -rho_max, rho_max, -rho_max, rho_max
    raise ValueError(f"Unsupported projection: {cfg.name}")


def forward_projection(lon_deg: np.ndarray, lat_deg: np.ndarray, cfg: ProjectionConfig):
    lon = lon_deg * DEG2RAD
    lat = lat_deg * DEG2RAD
    lon0 = cfg.center_lon
    lat0 = cfg.center_lat
    dlon = wrap_lon_rad(lon - lon0)

    if cfg.name == "equirectangular":
        x = dlon
        y = lat - lat0
        visible = (y >= -np.pi / 2) & (y <= np.pi / 2)
        return x, y, visible

    if cfg.name == "mercator":
        lat_lim = np.deg2rad(cfg.mercator_lat_limit_deg)
        lat_c = np.clip(lat, -lat_lim, lat_lim)
        y = np.log(np.tan(np.pi / 4 + lat_c / 2))
        x = dlon
        visible = np.isfinite(y)
        return x, y, visible

    sin_lat, cos_lat = np.sin(lat), np.cos(lat)
    sin_lat0, cos_lat0 = np.sin(lat0), np.cos(lat0)
    cos_c = sin_lat0 * sin_lat + cos_lat0 * cos_lat * np.cos(dlon)
    cos_c = np.clip(cos_c, -1.0, 1.0)
    c = np.arccos(cos_c)

    if cfg.name == "azimuthal_equidistant":
        k = np.ones_like(c)
        nz = c > 1e-12
        k[nz] = c[nz] / np.sin(c[nz])
        x = k * cos_lat * np.sin(dlon)
        y = k * (cos_lat0 * sin_lat - sin_lat0 * cos_lat * np.cos(dlon))
        visible = c <= np.pi + 1e-9
        return x, y, visible

    if cfg.name == "stereographic":
        denom = 1 + sin_lat0 * sin_lat + cos_lat0 * cos_lat * np.cos(dlon)
        visible = denom > 1e-9
        k = np.zeros_like(denom)
        k[visible] = 2.0 / denom[visible]
        x = k * cos_lat * np.sin(dlon)
        y = k * (cos_lat0 * sin_lat - sin_lat0 * cos_lat * np.cos(dlon))
        return x, y, visible

    raise ValueError(f"Unsupported projection: {cfg.name}")


def inverse_projection(x: np.ndarray, y: np.ndarray, cfg: ProjectionConfig):
    lon0 = cfg.center_lon
    lat0 = cfg.center_lat

    if cfg.name == "equirectangular":
        lon = wrap_lon_rad(lon0 + x)
        lat = lat0 + y
        visible = (lat >= -np.pi / 2) & (lat <= np.pi / 2)
        return lon * RAD2DEG, lat * RAD2DEG, visible

    if cfg.name == "mercator":
        lon = wrap_lon_rad(lon0 + x)
        lat = 2 * np.arctan(np.exp(y)) - np.pi / 2
        lat_lim = np.deg2rad(cfg.mercator_lat_limit_deg)
        visible = (lat >= -lat_lim) & (lat <= lat_lim)
        return lon * RAD2DEG, lat * RAD2DEG, visible

    rho = np.sqrt(x * x + y * y)
    c = rho.copy()

    if cfg.name == "stereographic":
        c = 2 * np.arctan2(rho, 2.0)
        cmax = np.deg2rad(cfg.stereographic_max_c_deg)
        visible = c <= cmax + 1e-9
    else:
        visible = rho <= np.pi + 1e-9

    sin_c = np.sin(c)
    cos_c = np.cos(c)
    sin_lat0, cos_lat0 = np.sin(lat0), np.cos(lat0)

    lat = np.full_like(x, lat0)
    lon = np.full_like(x, lon0)

    nz = rho > 1e-12
    lat[nz] = np.arcsin(
        np.clip(cos_c[nz] * sin_lat0 + (y[nz] * sin_c[nz] * cos_lat0) / rho[nz], -1.0, 1.0)
    )
    lon[nz] = lon0 + np.arctan2(
        x[nz] * sin_c[nz],
        rho[nz] * cos_lat0 * cos_c[nz] - y[nz] * sin_lat0 * sin_c[nz],
    )
    lon = wrap_lon_rad(lon)
    return lon * RAD2DEG, lat * RAD2DEG, visible
