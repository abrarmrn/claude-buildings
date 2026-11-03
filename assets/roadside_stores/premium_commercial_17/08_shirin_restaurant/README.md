# 08 - Shirin Restaurant

*C - Long-frontage restaurant* - status: **incomplete**

Massing: a long (46 m) but SHALLOW (14 m) sand-limestone frontage with ten tall arched windows and a bronze cornice, broken in the middle by an 11 m entrance tower carrying a tall pointed-arch portal and a back-lit bronze mashrabiya screen.  A 4.6 m deep terrace runs along the pavement: shaded on the left by a bronze pergola with lattice screens, open with a low stone balustrade on the right.  Inside: one tall (5.7 m) dining hall with lanterns, banquettes and a back-lit screen wall hiding the kitchen. Site: terrace directly on the pavement; optional side parking on the right (separate collection).

## Previews

![day](renders/shirin_restaurant_day.jpg)
![night](renders/shirin_restaurant_night.jpg)
![road_view](renders/shirin_restaurant_road_view.jpg)
![interior](renders/shirin_restaurant_interior.jpg)

## Key facts

| Item | Value |
|---|---|
| Storeys | 1 (+ 2-storey-high entrance tower) (floor levels [0.15] m, roof 7.2) |
| Frontage x depth x height | 46.0 x 16.0 x 11.2 m |
| LOD0 bounds (Blender) | - m |
| Setback from plot frontage | 0.0 m |
| Parking | optional right side, 5 bays (OPTIONAL_PARKING) |
| Vehicle access | terrace opens directly onto the pavement; separate right-hand crossing to optional parking |
| Glass | 10 arched PC_Glass windows + portal |
| Lights | None |
| Collision boxes | None |

## Files

- `shirin_restaurant.blend` - full editable Blender 4.5.15 LTS scene (textures referenced relatively from `textures/`).
- `shirin_restaurant.glb` - presentation export: LOD0/1/2 + site pieces + placeholder cars + lights + collision, textures embedded.
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
P08_<Title> (root, origin = centre of the plot frontage line, ground; front = -Y Blender / +Z glTF)
  LOD0/1/2 -> BUILDING_EXTERIOR, BUILDING_INTERIOR, GLASS_SYSTEM, FACADE_DETAILS, SIGNAGE, FURNITURE, DISPLAY_OBJECTS
  SIDEWALK_FRONTAGE, OPTIONAL_FORECOURT, DRIVEWAY, OPTIONAL_PARKING   (separate, removable site pieces)
  PLACEHOLDER_CARS (one object per car)   INTERIOR_LIGHTING   EXTERIOR_LIGHTING   COLLISION (*-convcolonly)
```

## Validation

- Result: **FAIL**; issues: None; warnings: None
- Degenerate faces: None; inverted faces in watertight pieces: None; vegetation: none
- Glass materials: None
- GLB re-import into a clean scene: None

Brand note: Original fictional brand (Latin + Arabic name).

Godot import has NOT been tested from the cloud session. If you copy this folder into a Godot project, delete or exclude the `.blend` (Godot would try to import it) - `textures/` and `renders/` contain `.gdignore`.
