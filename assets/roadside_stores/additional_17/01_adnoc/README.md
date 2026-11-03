# 01 - ADNOC Service Station

**Status:** complete (all validation checks passed, 4 renders produced)
**Recommended commercial placement:** Service station cluster (alternatives: E11 roadside). This is a reusable asset, not a geographic location.

## Files
| File | Purpose | Size |
|---|---|---:|
| `adnoc.glb` | Godot import file: all three LODs, collision proxies, night lights, embedded textures | 9.14 MiB |
| `adnoc.blend` | Editable Blender 4.5 LTS source (textures referenced from `textures/`) | 2.3 MiB |
| `lod/adnoc_lod0.glb` / `_lod1.glb` / `_lod2.glb` | Geometry-only exports of each LOD (no embedded textures), used to read back triangle counts | 4.55 / 1.03 / 0.21 MiB |
| `textures/` | Procedural PBR textures actually used (16 files, JPEG/PNG) | - |
| `renders/` | `adnoc_day.jpg`, `_night.jpg`, `_road_view.jpg`, `_detail.jpg` (1600x900 Blender/Cycles renders) | - |
| `validation.json` | Machine-readable results of every check listed below | - |

## Measured geometry (read back from the exported GLB)
| LOD | Triangles | Visibility range (Godot, via post-import script) |
|---|---:|---|
| LOD0 | 93,903 | 0 - 60 m |
| LOD1 | 17,126 | 60 - 170 m |
| LOD2 | 2,915 | 170 - 900 m |

LOD0 bounding box (plot incl. forecourt/parking, metres): **76.5 x 54.8 x 12.9** (X x Y x Z in Blender; width x depth x height).
Materials: 41 (7 brand-specific: ADN_Blue, ADN_BlueLED, ADN_BlueLit, ADN_Clad, ADN_Price, ADN_Red, ADN_SignWhite). Collision proxies: 23 convex boxes (`*-convcolonly`). Night lights: 20 glTF punctual lights (shadows off).

## Conventions (same as the three prototypes)
1 unit = 1 m - road-facing front is Blender -Y (glTF/Godot +Z) - origin at the plot centre at finished ground (z = 0) - transforms applied (geometry authored in final coordinates) -
hierarchy `root > <PREFIX>_LOD0/1/2 > merged part meshes`, plus `<PREFIX>_Collision` and `<PREFIX>_NightLights`.
To enable LOD switching in Godot assign `prototypes/roadside_lod_post_import.gd` (a verbatim copy is in `additional_17/`) as the import script. **Godot import has not been tested** from this cloud session.

## Day / night
Day: sun + sky, emissive sign faces stay readable. Night: emissive sign/glass/interior materials plus the `NightLights` collection (hidden in the day renders). Nothing is duplicated for night.

## Road-level sign readability (automatic check on the road-view camera)
- ADNOC canopy fascia wordmark: 33.4 px letter height at 1600x900, 100 % visible, readable
- ADNOC pylon wordmark: 11.9 px letter height at 1600x900, 100 % visible, not primary

## Branding
ADNOC wordmark + simplified round emblem (blue/white/red), OASIS shop sign; simplified recreation, not official artwork.

## Validation performed
Reopened the saved `.blend` in a fresh Blender process; mesh integrity (NaN, loose vertices, material indices, UVs), flipped-normal test (signed volume of every watertight piece), LOD objects and decreasing budgets, bounds, collision, materials and texture files; exported GLB parsed (triangles per LOD, embedded images decoded) and re-imported into a clean scene (meshes, triangles, bounds, textures). Results: `validation.json`.
Rebuild: `python _tools/build_01_adnoc.py` then `render_store.py` / `validate_store.py` (see BUILD_REPORT.md).
