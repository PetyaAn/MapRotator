"""Inverse-mapping renderer for rotated/reprojected world maps."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

from projections import ProjectionConfig, inverse_projection, projected_bounds
from rotation import rotate_lonlat


def _bilinear_sample_wrap_x(src: np.ndarray, sx: np.ndarray, sy: np.ndarray) -> np.ndarray:
    h, w, c = src.shape
    x0 = np.floor(sx).astype(np.int64)
    y0 = np.floor(sy).astype(np.int64)
    x1 = (x0 + 1) % w
    y1 = np.clip(y0 + 1, 0, h - 1)
    x0 = x0 % w
    y0 = np.clip(y0, 0, h - 1)

    wx = sx - np.floor(sx)
    wy = sy - np.floor(sy)

    p00 = src[y0, x0]
    p10 = src[y0, x1]
    p01 = src[y1, x0]
    p11 = src[y1, x1]

    top = p00 * (1 - wx)[..., None] + p10 * wx[..., None]
    bot = p01 * (1 - wx)[..., None] + p11 * wx[..., None]
    return top * (1 - wy)[..., None] + bot * wy[..., None]


def render_map(
    src_image: Image.Image,
    projection_cfg: ProjectionConfig,
    axis_lon_deg: float,
    axis_lat_deg: float,
    angle_deg: float,
    out_width: int,
    out_height: int,
    background_rgba: tuple[int, int, int, int] = (0, 0, 0, 0),
) -> Image.Image:
    src = np.asarray(src_image.convert("RGBA"), dtype=np.float32)
    src_h, src_w, _ = src.shape

    min_x, max_x, min_y, max_y = projected_bounds(projection_cfg)

    px = np.linspace(min_x, max_x, out_width, endpoint=False) + (max_x - min_x) / (2 * out_width)
    py = np.linspace(max_y, min_y, out_height, endpoint=False) - (max_y - min_y) / (2 * out_height)
    grid_x, grid_y = np.meshgrid(px, py)

    lon_r, lat_r, vis = inverse_projection(grid_x, grid_y, projection_cfg)
    lon_s, lat_s = rotate_lonlat(lon_r, lat_r, axis_lon_deg, axis_lat_deg, -angle_deg)

    sx = ((lon_s + 180.0) / 360.0) * src_w
    sy = ((90.0 - lat_s) / 180.0) * (src_h - 1)

    sampled = _bilinear_sample_wrap_x(src, sx, sy)

    out = np.zeros((out_height, out_width, 4), dtype=np.float32)
    out[:] = np.array(background_rgba, dtype=np.float32)

    valid = vis & np.isfinite(lon_s) & np.isfinite(lat_s)
    out[valid] = sampled[valid]

    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), mode="RGBA")


def write_metadata_json(
    out_path: str | Path,
    rotation: dict,
    projection: dict,
    output_size: dict,
) -> Path:
    out_path = Path(out_path)
    meta_path = out_path.with_suffix(out_path.suffix + ".metadata.json")
    payload = {
        "rotation": rotation,
        "projection": projection,
        "output": output_size,
    }
    meta_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return meta_path
