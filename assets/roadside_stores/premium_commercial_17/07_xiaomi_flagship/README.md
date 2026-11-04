# 07 - Xiaomi Flagship Store

*B - Technology flagship* - status: **complete**

Massing: compact two-storey box with a CHAMFERED right corner holding the entrance inside a big orange rounded-square portal (echoing the badge shape).  The front is a full-height glass wall overlaid by a staggered grid of proud white modular panels (~35 % cover) and slim orange fins, so the facade reads as a pixel pattern while most of the glass stays transparent.  Inside: phone islands, a TV wall, smart-home and wearables zones, e-scooters, an orange stair to an upper retail floor set back 2.5 m from the glass. Site: corner plaza at the entrance + optional small side car park on the left (separate collection).

## Previews

![day](renders/xiaomi_flagship_day.jpg)
![night](renders/xiaomi_flagship_night.jpg)
![road_view](renders/xiaomi_flagship_road_view.jpg)
![interior](renders/xiaomi_flagship_interior.jpg)

## Key facts

| Item | Value |
|---|---|
| Storeys | 2 (floor levels [0.15, 5.0] m, roof 9.6) |
| Frontage x depth x height | 26.0 x 20.0 x 10.6 m |
| LOD0 bounds (Blender) | [26.98, 20.92, 10.9] m |
| Setback from plot frontage | 5.0 m |
| Parking | optional left side car park, 6 bays (OPTIONAL_PARKING) |
| Vehicle access | left crossing to the small side car park; corner pedestrian plaza |
| Glass | full-height PC_Glass behind ~35 % modular panel cover |
| Lights | {'INTERIOR_LIGHTING': 5, 'EXTERIOR_LIGHTING': 1} |
| Collision boxes | 1 |

## Files

- `xiaomi_flagship.blend` - full editable Blender 4.5.15 LTS scene (textures referenced relatively from `textures/`).
- `xiaomi_flagship.glb` - presentation export: LOD0/1/2 + site pieces + placeholder cars + lights + collision, textures embedded.
- (no placeholder cars in this asset, so the main GLB is already building-only)
- `lod/` - geometry-only per-LOD GLBs used for independent triangle read-back (+ placeholder cars GLB where present), `build_stats.json`.
- `textures/` - procedural PBR maps (JPEG albedo/ORM/normal) + PNG brand/screen graphics.
- `renders/` - four 1600x900 Cycles JPEGs + `render_report.json` (ray-traced visibility checks).
- `validation.json` - fresh-process validation results.

## Triangles (read from the exported GLB)

| LOD0 | LOD1 | LOD2 | Placeholder cars | Site pieces | Collision |
|---|---|---|---|---|---|
| 14060 | 3898 | 1230 | 0 | 554 | 12 |

LOD visibility ranges (glTF extras, applied by `../premium_lod_post_import.gd`): {'LOD0': [0.0, 90.0], 'LOD1': [90.0, 260.0], 'LOD2': [260.0, 1600.0]}; placeholder cars 0-340 m.

## Hierarchy

```
P07_<Title> (root, origin = centre of the plot frontage line, ground; front = -Y Blender / +Z glTF)
  LOD0/1/2 -> BUILDING_EXTERIOR, BUILDING_INTERIOR, GLASS_SYSTEM, FACADE_DETAILS, SIGNAGE, FURNITURE, DISPLAY_OBJECTS
  SIDEWALK_FRONTAGE, OPTIONAL_FORECOURT, DRIVEWAY, OPTIONAL_PARKING   (separate, removable site pieces)
  PLACEHOLDER_CARS (one object per car)   INTERIOR_LIGHTING   EXTERIOR_LIGHTING   COLLISION (*-convcolonly)
```

## Validation

- Result: **PASS**; issues: []; warnings: []
- Degenerate faces: 10; inverted faces in watertight pieces: 0; vegetation: none
- Glass materials: {'PC_Glass': {'alpha': 0.16, 'blend': 'BLEND', 'double_sided': True}, 'PC_GlassClear': {'alpha': 0.11, 'blend': 'BLEND', 'double_sided': True}, 'PC_GlassRail': {'alpha': 0.14, 'blend': 'BLEND', 'double_sided': True}}
- GLB re-import into a clean scene: {'mesh_objects': 69, 'triangles': 19754, 'glb_triangles': 19754, 'images_loaded': 16, 'lights': 6, 'lod0_size_yup_converted': [26.98, 20.92, 10.9]}
- Ray-traced visibility from the road_view camera: cars readable 0/0 {}; interior probes reached 1/4 {'GF_tables': False, 'GF_front': True, 'L1_tables': False, 'L1_tvwall': False}
- Ray-traced visibility from the day camera: cars readable 0/0 {}; interior probes reached 2/4 {'GF_tables': True, 'GF_front': True, 'L1_tables': False, 'L1_tvwall': False}

Brand note: Orange rounded-square badge with "mi" in Inter Bold + "Xiaomi" wordmark (simplified recreation).

Godot import has NOT been tested from the cloud session. If you copy this folder into a Godot project, delete or exclude the `.blend` (Godot would try to import it) - `textures/` and `renders/` contain `.gdignore`.

## Brand signage correction

The brand identity was corrected on branch `claude/flagship-brand-fixes-boulevard-5`, and only the signage changed. Orange MI symbol (2.2 m) on the portal; lowercase "xiaomi" wordmark (3.6 m) as dark halo-lit letters on the white fascia. Artwork: Squircle + #ff6900 from mi.com; MI glyph simple-icons (source mi.com); wordmark typeset in MiSans (recreation). Old signage: `BRAND_SIGNAGE_ORIGINAL_DISABLED` collection in the .blend (not exported). New signage: `BRAND_SIGNAGE_CORRECTED` (+ `LOD1_` / `LOD2_`). Renders: `renders/xiaomi_flagship_signage_*.jpg`. Validation: `brand_signage_correction.json` (PASS). Provenance and permissions: `../FLAGSHIP_BRANDING_CORRECTION/BRAND_ASSET_SOURCES.md`. Internal test asset; no endorsement implied.
