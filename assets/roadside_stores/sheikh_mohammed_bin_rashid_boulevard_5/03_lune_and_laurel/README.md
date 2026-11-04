# Lune & Laurel Cafe - Premium cafe and patisserie (corner unit)

Boulevard podium asset 03 of 5 for a **Sheikh Mohammed bin Rashid Boulevard (Downtown Dubai)**-inspired street.
This is a fictional business for an internal test game: it is not a real shop, and no real tenant position or geographic
placement is implied. There is no vegetation (planters are empty).

## Architecture
Champagne-stone block whose street corner becomes a curved two-storey glass corner (4.2 m radius); arched-head recessed entrance under a cantilevered first-floor balcony; tall two-storey finned window; stepped parapet; gold script signage + corner blade sign.

## Interior
Marble-and-bronze coffee counter with espresso machines and lit pastry vitrines, cafe tables along the curved glass, bronze spiral stair to a first-floor lounge with sofas, armchairs and globe pendants.

## Dimensions (metres, Z-up, front = -Y in Blender = +Z in glTF)
| Item | Value |
|---|---|
| Frontage x depth | 16.0 x 15.0 |
| Height (top of podium / crown) | 10.92 |
| Commercial storeys | 2 |
| Floor levels | 0.15, 4.8 (roof slab 9.0) |
| Tower interface | rear plane y = 15.0, podium roof z = 10.92, interface top z = 12.12 (empty `B03_TOWER_INTERFACE`) |
| Origin | centre of the frontage line (building line), ground level; promenade strip at y < 0 |

## Files
| File | Size |
|---|---|
| `lune_and_laurel.blend` | 1.41 MB (editable source; build script `../_tools/build_03_*.py`) |
| `lune_and_laurel.glb` | 7.69 MB (Godot: all LODs, promenade + terrace pieces, lights, collision, embedded textures) |
| `lod/lune_and_laurel_lod0/1/2.glb` | 2.02 / 0.77 / 0.11 MB (geometry only) |
| `unreal/lune_and_laurel_LOD0/1/2.fbx` | 1.11 / 0.45 / 0.14 MB (Unreal; LOD0 includes `UCX_` collision; textures referenced relatively from `../textures`) |
| `textures/` | PBR maps (albedo / ORM / normal, 1024 px JPEG) |
| `renders/` | four Cycles renders, 1600x900 |
| `validation.json`, `lod/build_stats.json` | validation results / build statistics |

## Triangle counts (read from the exported GLB files)
| LOD | Triangles | Contents |
|---|---|---|
| LOD0 | 39,790 | full facade detail, interiors, furniture, signage (20,048 interior tris) |
| LOD1 | 12,838 | full shell + glass, slabs, stairs/escalators, simplified furniture (2,978 interior tris) |
| LOD2 | 1,371 | massing, coarse glazing, glow proxies, simplified signage |
| Full GLB total | 56,605 | incl. promenade, terrace pieces and collision boxes |

## Materials
41 materials. Stone: BV_Limestone / BV_Travertine / BV_Champagne / BV_BeigeStone (procedural large-format panels with
joints, roughness and normal maps); metal: BV_Bronze / BV_BronzeDark / BV_BlackFrame (metallic 1.0, roughness 0.3-0.35);
glass: BV_Glass / BV_GlassWarm (real alpha blend 0.11-0.12, double-sided, low tint, so the interiors stay visible). Lights:
6 interior + 3 exterior (KHR punctual).

## LOD recommendations
LOD0 0-110 m, LOD1 110-300 m, LOD2 300-1800 m (glTF node extras `visibility_range_*`, applied by
`../../premium_commercial_17/premium_lod_post_import.gd`). The glass facade and main entrance remain in every LOD. For Unreal
Engine 5, import LOD0 (Nanite-friendly) and use LOD1/LOD2 as HLOD inputs, with glass set to Translucent.

## Modular collections
`SIDEWALK_FRONTAGE` (promenade stone-paving strip, removable), `OPTIONAL_FORECOURT` (terrace + street furniture + empty planters: Small bistro deck with a parasol (optional collection); side-street paving.), `SIGNAGE`,
`COLLISION` (`*-convcolonly` boxes, 2 pieces). There is no parking or vegetation.

## Validation (Blender only)
Result: **PASS**. The `.blend` was reopened in a fresh process, and the checks were:
mesh.validate, degenerate faces, winding, UVs, material slots, glass alpha < 1, LOD order and extras, missing textures, and vegetation. The GLB
was then exported, parsed with every embedded image decoded, and re-imported into a clean scene
(56,605 triangles, matching 56,605). Interior visibility was ray-traced from
the day and road cameras (see `renders/render_report.json`). **Godot import has NOT been tested.** Unreal import has not been tested.
