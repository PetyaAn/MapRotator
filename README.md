# MapRotator

Small local tool to rotate a globe in 3D (Rodrigues rotation), then reproject and render to a flat map.

## Install

```bash
pip install -r requirements.txt
```

## CLI

```bash
python cli.py \
  --input world.png \
  --axis-preset custom \
  --axis-lon 0 \
  --axis-lat 0 \
  --angle 35 \
  --projection stereographic \
  --center-lon 0 \
  --center-lat 30 \
  --output-width-px 2000 \
  --output-height-px 2000 \
  --out rotated.png
```

Preset axes are available with `--axis-preset toward_0_0` and `--axis-preset toward_90e_0`.

The CLI writes both the output image and a metadata file:

- `rotated.png`
- `rotated.png.metadata.json`

## Web UI

```bash
streamlit run app.py
```

Features:
- Upload source map (PNG/JPG, expected equirectangular 2:1)
- Choose rotation angle and axis preset/custom lon/lat
- Choose projection and center
- Live downscaled preview
- Download full-resolution PNG and metadata JSON

## Tests

```bash
pytest -q
```

## Notes

- Supported projections: equirectangular, mercator, azimuthal equidistant, stereographic.
- Rendering uses inverse mapping and bilinear sampling.
- Longitude sampling wraps at the antimeridian for seam-safe output.
- PDF output can be produced by setting `--out file.pdf` (Pillow backend). SVG export is not included.
