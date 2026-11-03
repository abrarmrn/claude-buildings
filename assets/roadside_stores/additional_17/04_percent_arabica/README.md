# 04 - % Arabica

**Status:** complete (all validation checks passed, 4 renders produced)
**Recommended commercial placement:** Premium restaurant frontage (alternatives: Boulevard podium retail). This is a reusable asset, not a geographic location.

## Files
| File | Purpose | Size |
|---|---|---:|
| `percent_arabica.glb` | Godot import file: all three LODs, collision proxies, night lights, embedded textures | 4.95 MiB |
| `percent_arabica.blend` | Editable Blender 4.5 LTS source (textures referenced from `textures/`) | 0.76 MiB |
| `lod/percent_arabica_lod0.glb` / `_lod1.glb` / `_lod2.glb` | Geometry-only exports of each LOD (no embedded textures), used to read back triangle counts | 0.97 / 0.39 / 0.1 MiB |
| `textures/` | Procedural PBR textures actually used (14 files, JPEG/PNG) | - |
| `renders/` | `percent_arabica_day.jpg`, `_night.jpg`, `_road_view.jpg`, `_detail.jpg` (1600x900 Blender/Cycles renders) | - |
| `validation.json` | Machine-readable results of every check listed below | - |

## Measured geometry (read back from the exported GLB)
| LOD | Triangles | Visibility range (Godot, via post-import script) |
|---|---:|---|
| LOD0 | 21,511 | 0 - 60 m |
| LOD1 | 6,265 | 60 - 170 m |
| LOD2 | 1,222 | 170 - 900 m |

LOD0 bounding box (plot incl. forecourt/parking, metres): **43.0 x 32.2 x 7.9** (X x Y x Z in Blender; width x depth x height).
Materials: 32 (8 brand-specific: AR_Black, AR_Letter, AR_Menu, AR_Panel, AR_Warm, AR_White, AR_WhiteGlow, AR_Wood). Collision proxies: 12 convex boxes (`*-convcolonly`). Night lights: 13 glTF punctual lights (shadows off).

## Conventions (same as the three prototypes)
1 unit = 1 m - road-facing front is Blender -Y (glTF/Godot +Z) - origin at the plot centre at finished ground (z = 0) - transforms applied (geometry authored in final coordinates) -
hierarchy `root > <PREFIX>_LOD0/1/2 > merged part meshes`, plus `<PREFIX>_Collision` and `<PREFIX>_NightLights`.
To enable LOD switching in Godot assign `prototypes/roadside_lod_post_import.gd` (a verbatim copy is in `additional_17/`) as the import script. **Godot import has not been tested** from this cloud session.

## Day / night
Day: sun + sky, emissive sign faces stay readable. Night: emissive sign/glass/interior materials plus the `NightLights` collection (hidden in the day renders). Nothing is duplicated for night.

## Road-level sign readability (automatic check on the road-view camera)
- % ARABICA wall lockup: 18.3 px letter height at 1600x900, 100 % visible, readable
- % ARABICA stele lockup: 18.6 px letter height at 1600x900, 100 % visible, not primary

## Branding
Black "% ARABICA" in a light geometric sans on white; simplified recreation.

## Validation performed
Reopened the saved `.blend` in a fresh Blender process; mesh integrity (NaN, loose vertices, material indices, UVs), flipped-normal test (signed volume of every watertight piece), LOD objects and decreasing budgets, bounds, collision, materials and texture files; exported GLB parsed (triangles per LOD, embedded images decoded) and re-imported into a clean scene (meshes, triangles, bounds, textures). Results: `validation.json`.
Rebuild: `python _tools/build_04_arabica.py` then `render_store.py` / `validate_store.py` (see BUILD_REPORT.md).
