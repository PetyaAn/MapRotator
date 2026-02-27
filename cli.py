from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from projections import ProjectionConfig
from render import render_map, write_metadata_json


PRESET_AXES = {
    "toward_0_0": (0.0, 0.0),
    "toward_90e_0": (90.0, 0.0),
    "custom": None,
}


def parse_bg(value: str) -> tuple[int, int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) == 6:
        value += "FF"
    if len(value) != 8:
        raise argparse.ArgumentTypeError("Background must be RRGGBB or RRGGBBAA hex")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4, 6))


def resolve_axis(args) -> tuple[float, float]:
    if args.axis_preset != "custom":
        return PRESET_AXES[args.axis_preset]
    if args.axis_lon is None or args.axis_lat is None:
        raise ValueError("For --axis-preset custom, --axis-lon and --axis-lat are required")
    return args.axis_lon, args.axis_lat


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Rotate and reproject world maps")
    p.add_argument("--input", required=True, help="Input world map image (equirectangular, 2:1)")
    p.add_argument("--out", required=True, help="Output image path (.png/.jpg/.pdf)")
    p.add_argument("--angle", type=float, required=True, help="Rotation angle in degrees [0,180]")
    p.add_argument("--axis-preset", choices=list(PRESET_AXES.keys()), default="custom")
    p.add_argument("--axis-lon", type=float, default=None)
    p.add_argument("--axis-lat", type=float, default=None)

    p.add_argument(
        "--projection",
        required=True,
        choices=["equirectangular", "mercator", "azimuthal_equidistant", "stereographic"],
    )
    p.add_argument("--center-lon", type=float, default=0.0)
    p.add_argument("--center-lat", type=float, default=0.0)
    p.add_argument("--output-width-px", type=int, default=2048)
    p.add_argument("--output-height-px", type=int, default=1024)
    p.add_argument("--mercator-lat-limit", type=float, default=85.0)
    p.add_argument("--stereographic-max-c", type=float, default=170.0)
    p.add_argument("--background", type=parse_bg, default=(0, 0, 0, 0), help="Hex RRGGBB or RRGGBBAA")
    return p


def main() -> None:
    args = build_parser().parse_args()
    axis_lon, axis_lat = resolve_axis(args)

    src = Image.open(args.input)
    cfg = ProjectionConfig(
        name=args.projection,
        center_lon_deg=args.center_lon,
        center_lat_deg=args.center_lat,
        mercator_lat_limit_deg=args.mercator_lat_limit,
        stereographic_max_c_deg=args.stereographic_max_c,
    )
    out = render_map(
        src,
        cfg,
        axis_lon_deg=axis_lon,
        axis_lat_deg=axis_lat,
        angle_deg=args.angle,
        out_width=args.output_width_px,
        out_height=args.output_height_px,
        background_rgba=args.background,
    )

    out_path = Path(args.out)
    out.save(out_path)
    meta = write_metadata_json(
        out_path,
        rotation={
            "axis_lon": axis_lon,
            "axis_lat": axis_lat,
            "angle_deg": args.angle,
            "axis_preset": args.axis_preset,
        },
        projection={
            "name": args.projection,
            "center_lon": args.center_lon,
            "center_lat": args.center_lat,
            "mercator_lat_limit": args.mercator_lat_limit,
            "stereographic_max_c": args.stereographic_max_c,
        },
        output_size={"width": args.output_width_px, "height": args.output_height_px},
    )
    print(f"Wrote image: {out_path}")
    print(f"Wrote metadata: {meta}")


if __name__ == "__main__":
    main()
