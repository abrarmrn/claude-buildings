# BUILD REPORT - 17 additional roadside store assets

Generated 2026-11-03T17:30:44Z from files on disk (Blender 4.5.15 LTS via the `bpy` module, Cycles CPU renders, headless Linux cloud container).

**Result: 17/17 stores complete; 68 of 68 required 1600x900 JPEG renders exist.** Last completed asset: 17 Premium Auto Care.
Remaining / incomplete: none.

## Batches (processed sequentially as requested)

| Batch | Assets | Complete |
|---|---|---|
| A | 01, 02, 03, 04 | 01, 02, 03, 04 |
| B | 05, 06, 07, 08, 09 | 05, 06, 07, 08, 09 |
| C | 10, 11, 12, 13 | 10, 11, 12, 13 |
| D | 14, 15, 16, 17 | 14, 15, 16, 17 |

## Per-store measured results (triangles read back from the exported GLB)

| # | Store | Placement | LOD0 tris | LOD1 tris | LOD2 tris | GLB MiB | .blend MiB | Materials | Bounding box (m) | Sign px (road view) | Validation | Status |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---|
| 01 | ADNOC Service Station | Service station cluster | 93,903 | 17,126 | 2,915 | 9.14 | 2.3 | 41 | 76 x 55 x 12.9 | 33 | PASS | complete |
| 02 | Tim Hortons | Drive-through cluster | 42,655 | 13,066 | 2,237 | 6.55 | 1.49 | 47 | 59 x 45 x 8.9 | 34 | PASS | complete |
| 03 | Costa Coffee | Boulevard podium retail | 31,900 | 8,690 | 1,516 | 4.74 | 1.16 | 39 | 47 x 38 x 8.9 | 45 | PASS | complete |
| 04 | % Arabica | Premium restaurant frontage | 21,511 | 6,265 | 1,222 | 4.95 | 0.76 | 32 | 43 x 32 x 7.9 | 18 | PASS | complete |
| 05 | PAUL Bakery & Cafe | Boulevard podium retail | 29,938 | 9,479 | 1,918 | 5.59 | 1.01 | 41 | 39 x 28 x 9.7 | 34 | PASS | complete |
| 06 | Krispy Kreme | Drive-through cluster | 33,323 | 11,720 | 2,107 | 5.72 | 1.19 | 44 | 51 x 40 x 8.9 | 24 | PASS | complete |
| 07 | Baskin Robbins | General commercial retail | 28,994 | 9,332 | 1,707 | 5.39 | 1.03 | 40 | 41 x 32 x 9.0 | 40 | PASS | complete |
| 08 | McDonald's | Drive-through cluster | 37,483 | 11,735 | 2,170 | 5.96 | 1.24 | 45 | 67 x 50 x 9.8 | 91 | PASS | complete |
| 09 | KFC | Drive-through cluster | 32,533 | 10,265 | 1,519 | 5.58 | 1.06 | 39 | 59 x 44 x 8.9 | 38 | PASS | complete |
| 10 | Five Guys | Premium restaurant frontage | 25,874 | 9,718 | 1,239 | 4.65 | 0.93 | 34 | 43 x 32 x 8.4 | 29 | PASS | complete |
| 11 | Shake Shack | Premium restaurant frontage | 31,016 | 8,510 | 1,526 | 4.78 | 1.06 | 36 | 47 x 36 x 8.9 | 21 | PASS | complete |
| 12 | Subway | General commercial retail | 20,068 | 6,628 | 1,519 | 4.79 | 0.78 | 39 | 39 x 29 x 8.7 | 29 | PASS | complete |
| 13 | Pizza Hut | E11 roadside | 28,776 | 10,152 | 1,312 | 5.74 | 1.05 | 41 | 52 x 38 x 8.9 | 44 | PASS | complete |
| 14 | Operation Falafel | Boulevard podium retail | 43,242 | 15,698 | 1,769 | 6.23 | 1.5 | 36 | 43 x 33 x 11.2 | 30 | PASS | complete |
| 15 | Spinneys Market | General commercial retail | 100,818 | 14,400 | 2,397 | 11.87 | 2.31 | 45 | 68 x 46 x 8.9 | 36 | PASS | complete |
| 16 | Life Pharmacy | General commercial retail | 32,774 | 8,402 | 1,369 | 5.85 | 0.96 | 35 | 40 x 30 x 8.5 | 36 | PASS | complete |
| 17 | Premium Auto Care | E11 roadside | 32,289 | 13,223 | 1,616 | 4.91 | 1.2 | 42 | 55 x 42 x 8.8 | 23 | PASS | complete |

Totals: GLB 102.44 MiB, .blend 21.01 MiB, per-LOD GLBs 46.08 MiB.

## What was verified for every asset

- Saved `.blend`, reopened in a fresh background Blender process and inspected (integrity, UVs, materials, LOD objects, dimensions, collision, lights, extras).
- Flipped-normal test: every watertight mesh piece has positive signed volume (computed relative to the piece centroid in double precision after a float32 false-positive was found and fixed).
- GLB exported (master + three per-LOD geometry files); triangle counts parsed from the GLB JSON and matched to Blender; embedded textures decoded with Pillow; GLB re-imported into a clean scene and bounds/triangles/textures compared.
- Four 1600x900 JPEG renders per store (day, night, road view, detail) produced from the saved `.blend`.
- Road-view brand-sign check: the camera projects each registered sign (pixel height at 1600x900), ray-casts 10 points across the lettering for occlusion and checks the viewing angle. The check found and drove fixes to real problems (signs hidden by lamps/palms/porches, a lettering plane buried inside its sign box, an overhang covering a fascia).
- Visual inspection of every store (day/night/road/detail contact sheets) during production; fixes were applied before marking complete.

## Not verified / limitations (stated plainly)

- **Godot import was NOT tested.** The cloud session cannot reach the local project; conventions are copied from the three prototypes and the existing post-import script (see `roadside_lod_post_import.gd`, copied verbatim).
- Brand marks are **simplified procedural recreations**, not official logo artwork (see each README). Logos use Inter / Liberation / DejaVu fonts, extruded polygons and simple primitives. The KFC Colonel portrait and official script lettering (Tim Hortons, Krispy Kreme) are not reproduced.
- Interiors are shallow set dressing (shelves, counters, furniture silhouettes) intended to read through glass, not walkable interiors.
- Textures are procedural and tileable (1024 px JPEG q84 for generic materials); less rich than scanned PBR sets. Glass is alpha-blended (alpha 0.30), as in the prototypes.
- Lights in the GLB are tuned for the Cycles previews and will need re-tuning in Godot (shadows off).
- No exact real-world branch coordinates are used or implied; placement categories in the manifest are recommendations only.
- `lod/*.glb` are geometry-only (no embedded textures) to keep the repository small; the master `.glb` carries the textures.
- The `.blend` files sit next to the `.glb` (requested layout): if you copy whole store folders into a Godot project, either delete the `.blend` files or configure the Blender path, otherwise Godot will try to import them. `textures/` and `renders/` contain `.gdignore`; `PREVIEW_GALLERY/` deliberately has none.

## Render settings

Cycles (CPU, OpenImageDenoise), 1600x900, adaptive sampling, AgX view transform, 32-52 samples (denoised), Nishita sky + sun for day; blue-hour dusk world with moonlight and the `NightLights` collection for night. Cameras: 3/4 hero, driver height (1.25 m) road view, close facade/entrance/signage detail. Per-view render times are recorded in `STORE_ASSET_MANIFEST.json`.

## Reproducing

```bash
python3.11 -m venv venv && venv/bin/pip install bpy==4.5.15 pillow numpy arabic-reshaper python-bidi
cd assets/roadside_stores/additional_17/_tools
../../../../venv/bin/python build_01_adnoc.py          # one script per store (build_NN_*.py), writes .blend/.glb/lod/textures
../../../../venv/bin/python validate_store.py ../01_adnoc adnoc
../../../../venv/bin/python render_store.py ../01_adnoc adnoc   # 4 JPEGs in renders/
../../../../venv/bin/python make_reports.py                # gallery, catalog, manifest, READMEs, this report
```

The kit (`store_kit.py`) imports the prototypes' `roadside_lib.py` unchanged; the three original prototypes were not modified.
