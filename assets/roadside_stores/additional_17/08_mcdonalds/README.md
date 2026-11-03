# 08 - McDonald's

**Status:** complete (all validation checks passed, 4 renders produced)
**Recommended commercial placement:** Drive-through cluster (alternatives: E11 roadside). This is a reusable asset, not a geographic location.

## Files
| File | Purpose | Size |
|---|---|---:|
| `mcdonalds.glb` | Godot import file: all three LODs, collision proxies, night lights, embedded textures | 5.96 MiB |
| `mcdonalds.blend` | Editable Blender 4.5 LTS source (textures referenced from `textures/`) | 1.24 MiB |
| `lod/mcdonalds_lod0.glb` / `_lod1.glb` / `_lod2.glb` | Geometry-only exports of each LOD (no embedded textures), used to read back triangle counts | 1.65 / 0.71 / 0.16 MiB |
| `textures/` | Procedural PBR textures actually used (16 files, JPEG/PNG) | - |
| `renders/` | `mcdonalds_day.jpg`, `_night.jpg`, `_road_view.jpg`, `_detail.jpg` (1600x900 Blender/Cycles renders) | - |
| `validation.json` | Machine-readable results of every check listed below | - |

## Measured geometry (read back from the exported GLB)
| LOD | Triangles | Visibility range (Godot, via post-import script) |
|---|---:|---|
| LOD0 | 37,483 | 0 - 60 m |
| LOD1 | 11,735 | 60 - 170 m |
| LOD2 | 2,170 | 170 - 900 m |

LOD0 bounding box (plot incl. forecourt/parking, metres): **66.5 x 50.3 x 9.8** (X x Y x Z in Blender; width x depth x height).
Materials: 45 (10 brand-specific: MD_Grey, MD_LightGrey, MD_Menu, MD_Red, MD_RedLit, MD_Seat, MD_SeatY, MD_SignWhite ...). Collision proxies: 14 convex boxes (`*-convcolonly`). Night lights: 18 glTF punctual lights (shadows off).

## Conventions (same as the three prototypes)
1 unit = 1 m - road-facing front is Blender -Y (glTF/Godot +Z) - origin at the plot centre at finished ground (z = 0) - transforms applied (geometry authored in final coordinates) -
hierarchy `root > <PREFIX>_LOD0/1/2 > merged part meshes`, plus `<PREFIX>_Collision` and `<PREFIX>_NightLights`.
To enable LOD switching in Godot assign `prototypes/roadside_lod_post_import.gd` (a verbatim copy is in `additional_17/`) as the import script. **Godot import has not been tested** from this cloud session.

## Day / night
Day: sun + sky, emissive sign faces stay readable. Night: emissive sign/glass/interior materials plus the `NightLights` collection (hidden in the day renders). Nothing is duplicated for night.

## Road-level sign readability (automatic check on the road-view camera)
- McDonalds tower arches: 91.1 px letter height at 1600x900, 100 % visible, readable
- McDonalds wordmark: 17.1 px letter height at 1600x900, 100 % visible, not primary
- McDonalds pylon arches: 49.1 px letter height at 1600x900, 0 % visible, not primary

## Branding
Golden arches built as extruded arcs (simplified geometry, not the official artwork); red/yellow identity.

## Validation performed
Reopened the saved `.blend` in a fresh Blender process; mesh integrity (NaN, loose vertices, material indices, UVs), flipped-normal test (signed volume of every watertight piece), LOD objects and decreasing budgets, bounds, collision, materials and texture files; exported GLB parsed (triangles per LOD, embedded images decoded) and re-imported into a clean scene (meshes, triangles, bounds, textures). Results: `validation.json`.
Rebuild: `python _tools/build_08_mcdonalds.py` then `render_store.py` / `validate_store.py` (see BUILD_REPORT.md).
