# 17 - Premium Auto Care

**Status:** complete (all validation checks passed, 4 renders produced)
**Recommended commercial placement:** E11 roadside (alternatives: General commercial retail). This is a reusable asset, not a geographic location.

## Files
| File | Purpose | Size |
|---|---|---:|
| `premium_auto_care.glb` | Godot import file: all three LODs, collision proxies, night lights, embedded textures | 4.91 MiB |
| `premium_auto_care.blend` | Editable Blender 4.5 LTS source (textures referenced from `textures/`) | 1.2 MiB |
| `lod/premium_auto_care_lod0.glb` / `_lod1.glb` / `_lod2.glb` | Geometry-only exports of each LOD (no embedded textures), used to read back triangle counts | 1.56 / 0.77 / 0.13 MiB |
| `textures/` | Procedural PBR textures actually used (12 files, JPEG/PNG) | - |
| `renders/` | `premium_auto_care_day.jpg`, `_night.jpg`, `_road_view.jpg`, `_detail.jpg` (1600x900 Blender/Cycles renders) | - |
| `validation.json` | Machine-readable results of every check listed below | - |

## Measured geometry (read back from the exported GLB)
| LOD | Triangles | Visibility range (Godot, via post-import script) |
|---|---:|---|
| LOD0 | 32,289 | 0 - 60 m |
| LOD1 | 13,223 | 60 - 170 m |
| LOD2 | 1,616 | 170 - 900 m |

LOD0 bounding box (plot incl. forecourt/parking, metres): **55.4 x 42.0 x 8.8** (X x Y x Z in Blender; width x depth x height).
Materials: 42 (12 brand-specific: AC_Charcoal, AC_Dark, AC_Epoxy, AC_Foam, AC_LED, AC_Menu, AC_Orange, AC_OrangeLit ...). Collision proxies: 16 convex boxes (`*-convcolonly`). Night lights: 22 glTF punctual lights (shadows off).

## Conventions (same as the three prototypes)
1 unit = 1 m - road-facing front is Blender -Y (glTF/Godot +Z) - origin at the plot centre at finished ground (z = 0) - transforms applied (geometry authored in final coordinates) -
hierarchy `root > <PREFIX>_LOD0/1/2 > merged part meshes`, plus `<PREFIX>_Collision` and `<PREFIX>_NightLights`.
To enable LOD switching in Godot assign `prototypes/roadside_lod_post_import.gd` (a verbatim copy is in `additional_17/`) as the import script. **Godot import has not been tested** from this cloud session.

## Day / night
Day: sun + sky, emissive sign faces stay readable. Night: emissive sign/glass/interior materials plus the `NightLights` collection (hidden in the day renders). Nothing is duplicated for night.

## Road-level sign readability (automatic check on the road-view camera)
- PREMIUM AUTO CARE wordmark: 20.3 px letter height at 1600x900, 100 % visible, readable
- PREMIUM AUTO CARE pylon: 23.1 px letter height at 1600x900, 100 % visible, readable

## Branding
Generic (original) detailing-centre brand created for this asset; no third-party partnership implied.

## Validation performed
Reopened the saved `.blend` in a fresh Blender process; mesh integrity (NaN, loose vertices, material indices, UVs), flipped-normal test (signed volume of every watertight piece), LOD objects and decreasing budgets, bounds, collision, materials and texture files; exported GLB parsed (triangles per LOD, embedded images decoded) and re-imported into a clean scene (meshes, triangles, bounds, textures). Results: `validation.json`.
Rebuild: `python _tools/build_17_premium_auto_care.py` then `render_store.py` / `validate_store.py` (see BUILD_REPORT.md).
