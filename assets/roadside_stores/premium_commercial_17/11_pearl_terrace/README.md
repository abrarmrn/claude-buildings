# 11 - Pearl Terrace

*C - Long-frontage restaurant* - status: **incomplete**

Massing: a soft, pearl-white two-storey volume with fully rounded corners.  The upper dining room is wrapped by a deep cantilevered BALCONY TERRACE (rounded, 4 m projection on the front, 6 m over the side terrace) with a solid pearl parapet and a glass top rail; the ground floor sits back behind a full-height terrace-facing glass wall. A thin rounded roof canopy with a ring of LED floats above.  Footprint is wider than deep with a side garden terrace (empty stone planters only) under the balcony overhang. Inside: grand sweeping curved staircase, premium reception with a chandelier ring, visible upper floor. Site: terrace directly beside the pavement; no parking.

## Previews

![day](renders/pearl_terrace_day.jpg)
![night](renders/pearl_terrace_night.jpg)
![road_view](renders/pearl_terrace_road_view.jpg)
![interior](renders/pearl_terrace_interior.jpg)

## Key facts

| Item | Value |
|---|---|
| Storeys | 2 (floor levels [0.15, 5.2] m, roof 9.8) |
| Frontage x depth x height | 34.0 x 22.0 x 10.65 m |
| LOD0 bounds (Blender) | - m |
| Setback from plot frontage | 4.0 m |
| Parking | none (front + side terraces beside the pavement) |
| Vehicle access | pedestrian; no vehicle access |
| Glass | rounded champagne-framed PC_GlassClear walls on both floors |
| Lights | None |
| Collision boxes | None |

## Files

- `pearl_terrace.blend` - full editable Blender 4.5.15 LTS scene (textures referenced relatively from `textures/`).
- `pearl_terrace.glb` - presentation export: LOD0/1/2 + site pieces + placeholder cars + lights + collision, textures embedded.
- (no placeholder cars in this asset, so the main GLB is already building-only)
- `lod/` - geometry-only per-LOD GLBs used for independent triangle read-back (+ placeholder cars GLB where present), `build_stats.json`.
- `textures/` - procedural PBR maps (JPEG albedo/ORM/normal) + PNG brand/screen graphics.
- `renders/` - four 1600x900 Cycles JPEGs + `render_report.json` (ray-traced visibility checks).
- `validation.json` - fresh-process validation results.

## Triangles (read from the exported GLB)

| LOD0 | LOD1 | LOD2 | Placeholder cars | Site pieces | Collision |
|---|---|---|---|---|---|
| None | None | None | 0 | 0 | None |

LOD visibility ranges (glTF extras, applied by `../premium_lod_post_import.gd`): {}; placeholder cars 0-340 m.

## Hierarchy

```
P11_<Title> (root, origin = centre of the plot frontage line, ground; front = -Y Blender / +Z glTF)
  LOD0/1/2 -> BUILDING_EXTERIOR, BUILDING_INTERIOR, GLASS_SYSTEM, FACADE_DETAILS, SIGNAGE, FURNITURE, DISPLAY_OBJECTS
  SIDEWALK_FRONTAGE, OPTIONAL_FORECOURT, DRIVEWAY, OPTIONAL_PARKING   (separate, removable site pieces)
  PLACEHOLDER_CARS (one object per car)   INTERIOR_LIGHTING   EXTERIOR_LIGHTING   COLLISION (*-convcolonly)
```

## Validation

- Result: **FAIL**; issues: None; warnings: None
- Degenerate faces: None; inverted faces in watertight pieces: None; vegetation: none
- Glass materials: None
- GLB re-import into a clean scene: None

Brand note: Original fictional brand.

Godot import has NOT been tested from the cloud session. If you copy this folder into a Godot project, delete or exclude the `.blend` (Godot would try to import it) - `textures/` and `renders/` contain `.gdignore`.
