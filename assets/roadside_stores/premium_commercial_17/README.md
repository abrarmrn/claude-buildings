# Premium Commercial 17 (Dubai open world)

Seventeen premium, multi-storey commercial buildings with **real transparent glass and real 3D interiors** (showroom
cars, stores, restaurants, workshops, a four-storey mall), built with Blender 4.5.15 LTS via the Python API.
This collection is separate from the earlier 20 roadside stores (`../prototypes/`, `../additional_17/`), which are untouched.

- **See the results without Blender:** open `PREMIUM_COMMERCIAL_17_GALLERY.html` (works offline when kept next to the
  asset folders) or `PREMIUM_COMMERCIAL_17_CONTACT_SHEET.jpg`. Every asset has four real Cycles renders in `NN_*/renders/`
  (`*_day.jpg`, `*_night.jpg`, `*_road_view.jpg`, `*_interior.jpg`, 1600x900).
- Per asset folder: `<name>.blend` (editable scene), `<name>.glb` (presentation export with LOD0/1/2, site pieces,
  placeholder cars, lights, collision), `<name>_building_only.glb` (automotive assets: same without cars), `lod/`
  (geometry-only per-LOD GLBs + `build_stats.json`), `textures/`, `renders/`, `validation.json`, `README.md`.
- `PREMIUM_ASSET_MANIFEST.json` - dimensions, floors, measured GLB triangle counts, materials/textures, cars, validation.
- `BUILD_REPORT.md` - checkpoint, summary table, validation, LOD recommendations, known limitations.
- `premium_lod_post_import.gd` - Godot 4 post-import script (LOD visibility ranges from glTF extras, light groups,
  placeholder-car group). Derived from the earlier `roadside_lod_post_import.gd`, which is kept unchanged.
- `_tools/` - the generator: `pk_core.py` (asset container, materials, textures, export), `pk_arch.py` (curtain walls,
  slabs, stairs, escalators, railings), `pk_furn.py` (furniture, retail and workshop equipment), `pk_cars.py`
  (generic placeholder vehicles), `pk_site.py` (pavement, driveways, parking, preview street), one
  `build_NN_*.py` per building, `validate_asset.py`, `render_asset.py`, `make_reports.py`, `run_batch.sh`.

Rebuild one asset: `python _tools/build_NN_name.py` (Python 3.11 with `pip install bpy==4.5.15 numpy pillow arabic-reshaper python-bidi`),
then `python _tools/validate_asset.py NN_folder base` and `python _tools/render_asset.py NN_folder base`.

Conventions: metres, Z up, road-facing front = Blender -Y (= glTF/Godot +Z), origin at the centre of the plot frontage
line (back edge of the 4 m public pavement) at ground level. No vegetation anywhere (planters are empty structures).
Vehicle access is always from the service road, never from the main carriageway.

Godot import has **not** been tested (the cloud session cannot reach the local Godot projects, which were not touched).
Real-world brand marks are simplified generic recreations, not official artwork.
