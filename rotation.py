"""Spherical rotation utilities using 3D vectors and Rodrigues' formula."""

from __future__ import annotations

import numpy as np


def lonlat_to_xyz(lon_deg: np.ndarray, lat_deg: np.ndarray) -> np.ndarray:
    lon = np.deg2rad(lon_deg)
    lat = np.deg2rad(lat_deg)
    cos_lat = np.cos(lat)
    x = cos_lat * np.cos(lon)
    y = cos_lat * np.sin(lon)
    z = np.sin(lat)
    return np.stack([x, y, z], axis=-1)


def xyz_to_lonlat(xyz: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    xyz = xyz / np.linalg.norm(xyz, axis=-1, keepdims=True)
    x = xyz[..., 0]
    y = xyz[..., 1]
    z = xyz[..., 2]
    lon = np.rad2deg(np.arctan2(y, x))
    lat = np.rad2deg(np.arcsin(np.clip(z, -1.0, 1.0)))
    lon = ((lon + 180.0) % 360.0) - 180.0
    return lon, lat


def axis_from_lonlat(axis_lon_deg: float, axis_lat_deg: float) -> np.ndarray:
    axis = lonlat_to_xyz(np.array(axis_lon_deg), np.array(axis_lat_deg))
    axis = np.asarray(axis, dtype=np.float64)
    axis /= np.linalg.norm(axis)
    return axis


def rodrigues_matrix(axis: np.ndarray, angle_deg: float) -> np.ndarray:
    axis = np.asarray(axis, dtype=np.float64)
    axis = axis / np.linalg.norm(axis)
    ax, ay, az = axis
    theta = np.deg2rad(angle_deg)
    c = np.cos(theta)
    s = np.sin(theta)
    k = np.array([[0.0, -az, ay], [az, 0.0, -ax], [-ay, ax, 0.0]])
    i = np.eye(3)
    outer = np.outer(axis, axis)
    return c * i + (1.0 - c) * outer + s * k


def rotate_lonlat(
    lon_deg: np.ndarray,
    lat_deg: np.ndarray,
    axis_lon_deg: float,
    axis_lat_deg: float,
    angle_deg: float,
) -> tuple[np.ndarray, np.ndarray]:
    xyz = lonlat_to_xyz(lon_deg, lat_deg)
    r = rodrigues_matrix(axis_from_lonlat(axis_lon_deg, axis_lat_deg), angle_deg)
    rotated = xyz @ r.T
    return xyz_to_lonlat(rotated)
