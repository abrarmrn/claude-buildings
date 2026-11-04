# Flagship brand signage correction - report

Generated 2026-11-04T06:23Z from the files on disk. Blender 4.5.15 LTS (bpy), Cycles CPU.

**Scope:** only signage was changed in `01`-`07`. Building geometry, interiors, placeholder cars, glass, lighting, materials not related to signage, LOD structure and collision are untouched. Every re-exported GLB was diffed node-by-node against the original commit: **all non-signage nodes have identical triangle counts and the lights are unchanged** (`brand_fix_validation.json`).

Overall Blender validation: **PASS**. Godot import has NOT been tested (the cloud session cannot reach the local Godot projects, which were not touched).

| # | Brand | Corrected marks | Artwork source | LOD0 / LOD1 / LOD2 sign tris | GLB tris before -> after | Validation |
|---|---|---|---|---|---|---|
| 01 | Mercedes-Benz | Dimensional three-pointed star in ring on the granite core (4.0 m), official wordmark on the roof plate (11.0 m) and under the star (3.4 m). | Star: simple-icons 5.0.0 (source mercedes-benz.com). Wordmark: official 1792 px image from mercedes-benz.com, potrace-vectorised. | 7,550 / 3,878 / 18 | 67,723 -> 73,252 | PASS |
| 02 | BMW | Dealership roundel (black ring, white letters, blue/white quarters, chrome rims) on the blade (3.8 m) and pylon (2.3 m). | simple-icons bmw (source bmw.com); physical-emblem colours composed from that vector. | 4,252 / 2,212 / 4 | 50,460 -> 47,360 | PASS |
| 03 | Porsche | Official PORSCHE wordmark on the upper box fascia (7.5 m); coloured crest (1.22 m) + wordmark (3.5 m) on the forecourt monolith. | Wordmark: Porsche Design System (official vector). Crest: simple-icons line-art coloured from the official 2023 crest image (recreation). | 1,772 / 1,124 / 6 | 42,362 -> 42,322 | PASS |
| 04 | Ford | Blue Oval (7.4 x 2.78 m) with raised white script and rim on the portal; supporting SERVICE / PARTS texts re-set in Inter. | ford.com navigation logo SVG (official vector, #00095B). | 3,984 / 1,916 / 2 | 46,521 -> 49,120 | PASS |
| 05 | Samsung | SAMSUNG wordmark (4.9 m, white reversed on the black fascia) as illuminated channel letters; EXPERIENCE STORE line re-set in Inter. | simple-icons samsung (source samsung.com brand identity). | 1,188 / 676 / 2 | 20,015 -> 19,668 | PASS |
| 06 | Apple | Illuminated Apple logo (1.95 m) suspended behind the glass on the existing rod + small flank logo (1.0 m); no store-name text. | apple.com global navigation SVG (official vector). | 836 / 376 / 4 | 19,640 -> 20,844 | PASS |
| 07 | Xiaomi | Orange MI symbol (2.2 m) on the portal; lowercase "xiaomi" wordmark (3.6 m) as dark halo-lit letters on the white fascia. | Squircle + #ff6900 from mi.com; MI glyph simple-icons (source mi.com); wordmark typeset in MiSans (recreation). | 1,928 / 1,040 / 4 | 19,754 -> 20,970 | PASS |

## Files changed in each flagship folder

- `<base>.blend`: old brand objects moved to the excluded `BRAND_SIGNAGE_ORIGINAL_DISABLED` collection (mounting structures kept as `<P>_LODn_SIGNAGE_Mounting`), plus the new `BRAND_SIGNAGE_CORRECTED` / `LOD1_` / `LOD2_` collections
- `<base>.glb`, `<base>_building_only.glb` (automotive), `lod/<base>_lod0/1/2.glb`: re-exported with the original exporter settings
- `textures/brand_*.png`: vector-rendered sign textures (LOD2 cards, Porsche crest face)
- `renders/<base>_signage_front_day.jpg`, `_front_night.jpg`, `_road.jpg` (+ Porsche `_detail_day.jpg`): new targeted renders
- `brand_signage_correction.json`: per-asset validation, measured sign sizes, GLB diff
- `README.md`: a "Brand signage correction" section appended

Not changed: `validation.json`, `lod/build_stats.json`, the original four renders, `../PREMIUM_ASSET_MANIFEST.json` and `../BUILD_REPORT.md`. These still describe the original build, and their signage triangle counts are superseded by the numbers here. The old procedural logo PNGs stay in `textures/` (no longer referenced).

## Validation performed

1. Each `.blend` reopened in a fresh Blender process: corrected collections are present and nested in LOD0/1/2, the original signage is excluded from the view layer and is outside the export tree, and no old `_SIGNAGE_Brand` object is still exported.
2. `Mesh.validate()` was run on every corrected sign object, with no empty material slots and UVs present.
3. Logo proportions: the width/height of every LOD0 sign was measured in the sign plane and compared with the ink bounds of its source vector. The maximum error is 0.14 %.
4. Spelling: all wordmarks are the brand vectors themselves (no typed text). The supporting texts are "SERVICE", "PARTS & SERVICE RECEPTION" and "EXPERIENCE STORE".
5. GLB diff against the original commit (main, building-only and the per-LOD files).
6. Targeted Cycles renders: front day, front night and road level, plus a before view rendered from the original `.blend`.

See `BRAND_ASSET_SOURCES.md` for provenance, known gaps and permissions.
