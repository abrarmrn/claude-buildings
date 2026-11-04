# Galerie D'Or - High-end fashion and lifestyle retail gallery

Boulevard podium asset 04 of 5 for a **Sheikh Mohammed bin Rashid Boulevard (Downtown Dubai)**-inspired street.
This is a fictional business for an internal test game: it is not a real shop, and no real tenant position or geographic
placement is implied. There is no vegetation (planters are empty).

## Architecture
Beige-stone podium with four different boutique shopfronts (projecting vitrine / horizontal bronze bands / vertical bronze fins / framed pane on granite riser), central recessed entrance below a bronze bay window, punched upper windows with bronze surrounds, fluted attic.

## Interior
Four boutiques with mannequins, clothes rails, display cases, wall shelving and seating behind glass hall partitions; central atrium with a wide stone stair to an open upper gallery with chandelier rings.

## Dimensions (metres, Z-up, front = -Y in Blender = +Z in glTF)
| Item | Value |
|---|---|
| Frontage x depth | 26.0 x 22.0 |
| Height (top of podium / crown) | 11.85 |
| Commercial storeys | 2 |
| Floor levels | 0.15, 5.6 (roof slab 10.2) |
| Tower interface | rear plane y = 22.0, podium roof z = 11.85, interface top z = 13.25 (empty `B04_TOWER_INTERFACE`) |
| Origin | centre of the frontage line (building line), ground level; promenade strip at y < 0 |

## Files
| File | Size |
|---|---|
| `galerie_dor.blend` | 1.54 MB (editable source; build script `../_tools/build_04_*.py`) |
| `galerie_dor.glb` | 9.07 MB (Godot: all LODs, promenade + terrace pieces, lights, collision, embedded textures) |
| `lod/galerie_dor_lod0/1/2.glb` | 2.51 / 1.13 / 0.14 MB (geometry only) |
| `unreal/galerie_dor_LOD0/1/2.fbx` | 1.15 / 0.6 / 0.19 MB (Unreal; LOD0 includes `UCX_` collision; textures referenced relatively from `../textures`) |
| `textures/` | PBR maps (albedo / ORM / normal, 1024 px JPEG) |
| `renders/` | four Cycles renders, 1600x900 |
| `validation.json`, `lod/build_stats.json` | validation results / build statistics |

## Triangle counts (read from the exported GLB files)
| LOD | Triangles | Contents |
|---|---|---|
| LOD0 | 44,564 | full facade detail, interiors, furniture, signage (21,680 interior tris) |
| LOD1 | 18,556 | full shell + glass, slabs, stairs/escalators, simplified furniture (5,420 interior tris) |
| LOD2 | 1,420 | massing, coarse glazing, glow proxies, simplified signage |
| Full GLB total | 65,640 | incl. promenade, terrace pieces and collision boxes |

## Materials
51 materials. Stone: BV_Limestone / BV_Travertine / BV_Champagne / BV_BeigeStone (procedural large-format panels with
joints, roughness and normal maps); metal: BV_Bronze / BV_BronzeDark / BV_BlackFrame (metallic 1.0, roughness 0.3-0.35);
glass: BV_Glass / BV_GlassWarm (real alpha blend 0.11-0.12, double-sided, low tint, so the interiors stay visible). Lights:
12 interior + 5 exterior (KHR punctual).

## LOD recommendations
LOD0 0-110 m, LOD1 110-300 m, LOD2 300-1800 m (glTF node extras `visibility_range_*`, applied by
`../../premium_commercial_17/premium_lod_post_import.gd`). The glass facade and main entrance remain in every LOD. For Unreal
Engine 5, import LOD0 (Nanite-friendly) and use LOD1/LOD2 as HLOD inputs, with glass set to Translucent.

## Modular collections
`SIDEWALK_FRONTAGE` (promenade stone-paving strip, removable), `OPTIONAL_FORECOURT` (terrace + street furniture + empty planters: None - benches, bollards, empty planters only.), `SIGNAGE`,
`COLLISION` (`*-convcolonly` boxes, 3 pieces). There is no parking or vegetation.

## Validation (Blender only)
Result: **PASS**. The `.blend` was reopened in a fresh process, and the checks were:
mesh.validate, degenerate faces, winding, UVs, material slots, glass alpha < 1, LOD order and extras, missing textures, and vegetation. The GLB
was then exported, parsed with every embedded image decoded, and re-imported into a clean scene
(65,640 triangles, matching 65,640). Interior visibility was ray-traced from
the day and road cameras (see `renders/render_report.json`). **Godot import has NOT been tested.** Unreal import has not been tested.
