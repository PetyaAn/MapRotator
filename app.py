from __future__ import annotations

import io
import json

import streamlit as st
from PIL import Image

from projections import ProjectionConfig
from render import render_map

PRESET_AXES = {
    "shift pole toward lon=0,lat=0": (0.0, 0.0),
    "shift pole toward lon=90E,lat=0": (90.0, 0.0),
    "custom axis": None,
}

st.set_page_config(page_title="Map Rotator", layout="wide")
st.title("World Map Pole Rotator + Reprojector")

uploaded = st.file_uploader("Upload equirectangular world image (PNG/JPG)", type=["png", "jpg", "jpeg"])

col1, col2 = st.columns(2)
with col1:
    angle = st.slider("rotation_angle_degrees", min_value=0.0, max_value=180.0, value=30.0, step=0.5)
    preset = st.selectbox("rotation axis preset", list(PRESET_AXES.keys()))
    axis_lon = st.number_input("axis_lon", min_value=-180.0, max_value=180.0, value=0.0, step=1.0)
    axis_lat = st.number_input("axis_lat", min_value=-90.0, max_value=90.0, value=0.0, step=1.0)

with col2:
    projection = st.selectbox(
        "projection_name",
        ["equirectangular", "mercator", "azimuthal_equidistant", "stereographic"],
    )
    center_lon = st.number_input("center_lon", min_value=-180.0, max_value=180.0, value=0.0, step=1.0)
    center_lat = st.number_input("center_lat", min_value=-90.0, max_value=90.0, value=0.0, step=1.0)
    out_w = st.number_input("output_width_px", min_value=128, max_value=8192, value=1600, step=64)
    out_h = st.number_input("output_height_px", min_value=128, max_value=8192, value=800, step=64)

if preset != "custom axis":
    axis_lon, axis_lat = PRESET_AXES[preset]

if uploaded is not None:
    src = Image.open(uploaded)
    st.caption(f"Input size: {src.width}x{src.height}")

    cfg = ProjectionConfig(
        name=projection,
        center_lon_deg=center_lon,
        center_lat_deg=center_lat,
    )

    preview = render_map(
        src,
        cfg,
        axis_lon_deg=axis_lon,
        axis_lat_deg=axis_lat,
        angle_deg=angle,
        out_width=max(256, int(out_w // 3)),
        out_height=max(128, int(out_h // 3)),
    )
    st.image(preview, caption="Live preview (downscaled)", use_container_width=True)

    if st.button("Render full resolution"):
        full = render_map(
            src,
            cfg,
            axis_lon_deg=axis_lon,
            axis_lat_deg=axis_lat,
            angle_deg=angle,
            out_width=int(out_w),
            out_height=int(out_h),
        )
        buf = io.BytesIO()
        full.save(buf, format="PNG")
        st.download_button("Download PNG", data=buf.getvalue(), file_name="rotated_map.png", mime="image/png")

        metadata = {
            "rotation": {"axis_lon": axis_lon, "axis_lat": axis_lat, "angle_deg": angle, "axis_preset": preset},
            "projection": {
                "name": projection,
                "center_lon": center_lon,
                "center_lat": center_lat,
            },
            "output": {"width": int(out_w), "height": int(out_h)},
        }
        st.download_button(
            "Download metadata JSON",
            data=json.dumps(metadata, indent=2),
            file_name="rotated_map.metadata.json",
            mime="application/json",
        )
