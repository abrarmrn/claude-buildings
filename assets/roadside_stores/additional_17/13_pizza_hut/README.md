# 13 - Pizza Hut

**Status:** complete (all validation checks passed, 4 renders produced)
**Recommended commercial placement:** E11 roadside (alternatives: Drive-through cluster). This is a reusable asset, not a geographic location.

## Files
| File | Purpose | Size |
|---|---|---:|
| `pizza_hut.glb` | Godot import file: all three LODs, collision proxies, night lights, embedded textures | 5.74 MiB |
| `pizza_hut.blend` | Editable Blender 4.5 LTS source (textures referenced from `textures/`) | 1.05 MiB |
| `lod/pizza_hut_lod0.glb` / `_lod1.glb` / `_lod2.glb` | Geometry-only exports of each LOD (no embedded textures), used to read back triangle counts | 1.3 / 0.61 / 0.11 MiB |
| `textures/` | Procedural PBR textures actually used (20 files, JPEG/PNG) | - |
| `renders/` | `pizza_hut_day.jpg`, `_night.jpg`, `_road_view.jpg`, `_detail.jpg` (1600x900 Blender/Cycles renders) | - |
| `validation.json` | Machine-readable results of every check listed below | - |

## Measured geometry (read back from the exported GLB)
| LOD | Triangles | Visibility range (Godot, via post-import script) |
|---|---:|---|
| LOD0 | 28,776 | 0 - 60 m |
| LOD1 | 10,152 | 60 - 170 m |
| LOD2 | 1,312 | 170 - 900 m |

LOD0 bounding box (plot incl. forecourt/parking, metres): **51.5 x 37.8 x 8.9** (X x Y x Z in Blender; width x depth x height).
Materials: 41 (9 brand-specific: PH_Booth, PH_Cream, PH_Dark, PH_Menu, PH_Oven, PH_Red, PH_RedLit, PH_Roof ...). Collision proxies: 10 convex boxes (`*-convcolonly`). Night lights: 14 glTF punctual lights (shadows off).

## Conventions (same as the three prototypes)
1 unit = 1 m - road-facing front is Blender -Y (glTF/Godot +Z) - origin at the plot centre at finished ground (z = 0) - transforms applied (geometry authored in final coordinates) -
hierarchy `root > <PREFIX>_LOD0/1/2 > merged part meshes`, plus `<PREFIX>_Collision` and `<PREFIX>_NightLights`.
To enable LOD switching in Godot assign `prototypes/roadside_lod_post_import.gd` (a verbatim copy is in `additional_17/`) as the import script. **Godot import has not been tested** from this cloud session.

## Day / night
Day: sun + sky, emissive sign faces stay readable. Night: emissive sign/glass/interior materials plus the `NightLights` collection (hidden in the day renders). Nothing is duplicated for night.

## Road-level sign readability (automatic check on the road-view camera)
- Pizza Hut roof-slope logo: 24.5 px letter height at 1600x900, 100 % visible, readable
- Pizza Hut pole sign: 43.6 px letter height at 1600x900, 100 % visible, readable

## Branding
Red-roof silhouette with white wordmark; simplified recreation, not the official logo.

## Validation performed
Reopened the saved `.blend` in a fresh Blender process; mesh integrity (NaN, loose vertices, material indices, UVs), flipped-normal test (signed volume of every watertight piece), LOD objects and decreasing budgets, bounds, collision, materials and texture files; exported GLB parsed (triangles per LOD, embedded images decoded) and re-imported into a clean scene (meshes, triangles, bounds, textures). Results: `validation.json`.
Rebuild: `python _tools/build_13_pizza_hut.py` then `render_store.py` / `validate_store.py` (see BUILD_REPORT.md).
