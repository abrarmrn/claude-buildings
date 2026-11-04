# Flagship branding correction (premium_commercial_17 / 01-07)

This folder corrects the brand signage of the seven flagship buildings: Mercedes-Benz, BMW, Porsche, Ford, Samsung, Apple and Xiaomi.
**Only the signage changed.** The buildings, interiors, cars, glass, lighting, LOD structure and collision were not modified, and
the 10 non-flagship premium assets and the 20 roadside stores were not touched.

- `FLAGSHIP_BRANDING_CORRECTION_GALLERY.html` shows before / after / night / road views for each brand. It works offline when this
  folder stays next to the `0N_*` asset folders.
- `FLAGSHIP_BRANDING_CORRECTIONS.jpg` is the same comparison as one contact sheet.
- `BRAND_ASSET_SOURCES.md` lists where every logo came from, the colour values, the known gaps, and the **permissions needed
  before any public or commercial use**.
- `BRAND_CORRECTION_REPORT.md` has the per-brand summary, the files changed in each flagship folder, and the validation results.
- `brand_fix_validation.json` holds the machine-readable validation: fresh-process reopen checks, measured logo proportions, and a
  node-by-node GLB diff against the original commit.
- `source_vectors/original/` holds the downloaded artwork. `source_vectors/final/` holds the normalised layered SVGs (+ `logo_manifest.json`).
- `textures/` holds high-resolution vector renders (PNG) and `logo_library_preview.jpg`.
- `renders/NN_before_front_day.jpg` are the "before" views, rendered from the pre-correction `.blend` with the same camera as the
  "after" views in `../0N_*/renders/*_signage_*.jpg`.
- `_tools/` contains the scripts:
  - `build_logo_library.py`: vectors to layered SVG + PNG (CPython 3.11 with cairosvg, svgelements, potracer, fonttools, scipy)
  - `apply_brand_fix.py NN`: in-place signage swap in the `.blend` + GLB re-export (Blender 4.5.15 `bpy`; svgelements on `BR_PYLIB`)
  - `render_signage.py NN view` and `run_signage_renders.sh`: targeted Cycles renders
  - `validate_brand_fix.py <orig_glb_root>`: validation
  - `make_brand_report.py`: gallery, contact sheet and reports
  - `glb_stats.py`: dependency-free GLB inspector

## Structure inside each flagship `.blend`

| Collection | Contents | Exported |
|---|---|---|
| `LOD0 / BRAND_SIGNAGE_CORRECTED` | extruded vector signs (fine curve tolerance 1.5 mm), illuminated faces, metal returns, mounting rail | yes, under `<P>_LOD0` |
| `LOD1 / LOD1_BRAND_SIGNAGE_CORRECTED` | the same signs at 6 mm curve tolerance | yes, under `<P>_LOD1` |
| `LOD2 / LOD2_BRAND_SIGNAGE_CORRECTED` | one alpha-clipped emissive card per sign, rendered from the same vector (exact silhouette and colours, 2 triangles) | yes, under `<P>_LOD2` |
| `<P>_LODn_SIGNAGE_Mounting` (BMW pylon, Porsche monolith, Apple hanger rod) | original mounting structures, kept in place | yes |
| `BRAND_SIGNAGE_ORIGINAL_DISABLED` | the old artwork, unparented and excluded from the view layer | **no** (delete it at will; git history also holds the original) |

Blender-validated only. **Godot import has not been tested** from this cloud session.
