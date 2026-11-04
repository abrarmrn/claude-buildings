# Juniper House - Luxury international restaurant

Boulevard podium asset 02 of 5 for a **Sheikh Mohammed bin Rashid Boulevard (Downtown Dubai)**-inspired street.
This is a fictional business for an internal test game: it is not a real shop, and no real tenant position or geographic
placement is implied. There is no vegetation (planters are empty).

## Architecture
Long, low horizontal frontage: slender travertine mullion-piers on a 3 m grid with 6.2 m continuous glass; three recessed entrance bays (6 m central); a 4.6 m deep bronze canopy running the full 30 m; stepped crown with a vertical bronze fin screen.

## Interior
Double-height hall with a walnut rib ceiling and light lines, central island bar with lit back bar, banquettes and table rows; rear mezzanine dining with glass balustrade and open stair.

## Dimensions (metres, Z-up, front = -Y in Blender = +Z in glTF)
| Item | Value |
|---|---|
| Frontage x depth | 30.0 x 20.0 |
| Height (top of podium / crown) | 9.7 |
| Commercial storeys | 1 (one tall floor (7.6 m) + rear mezzanine) |
| Floor levels | 0.15, 4.4 (roof slab 7.6) |
| Tower interface | rear plane y = 20.0, podium roof z = 9.7, interface top z = 11.7 (empty `B02_TOWER_INTERFACE`) |
| Origin | centre of the frontage line (building line), ground level; promenade strip at y < 0 |

## Files
| File | Size |
|---|---|
| `juniper_house.blend` | 2.05 MB (editable source; build script `../_tools/build_02_*.py`) |
| `juniper_house.glb` | 9.61 MB (Godot: all LODs, promenade + terrace pieces, lights, collision, embedded textures) |
| `lod/juniper_house_lod0/1/2.glb` | 3.06 / 1.08 / 0.13 MB (geometry only) |
| `unreal/juniper_house_LOD0/1/2.fbx` | 1.64 / 0.54 / 0.18 MB (Unreal; LOD0 includes `UCX_` collision; textures referenced relatively from `../textures`) |
| `textures/` | PBR maps (albedo / ORM / normal, 1024 px JPEG) |
| `renders/` | four Cycles renders, 1600x900 |
| `validation.json`, `lod/build_stats.json` | validation results / build statistics |

## Triangle counts (read from the exported GLB files)
| LOD | Triangles | Contents |
|---|---|---|
| LOD0 | 66,840 | full facade detail, interiors, furniture, signage (44,830 interior tris) |
| LOD1 | 18,102 | full shell + glass, slabs, stairs/escalators, simplified furniture (7,048 interior tris) |
| LOD2 | 1,452 | massing, coarse glazing, glow proxies, simplified signage |
| Full GLB total | 95,766 | incl. promenade, terrace pieces and collision boxes |

## Materials
39 materials. Stone: BV_Limestone / BV_Travertine / BV_Champagne / BV_BeigeStone (procedural large-format panels with
joints, roughness and normal maps); metal: BV_Bronze / BV_BronzeDark / BV_BlackFrame (metallic 1.0, roughness 0.3-0.35);
glass: BV_Glass / BV_GlassWarm (real alpha blend 0.11-0.12, double-sided, low tint, so the interiors stay visible). Lights:
8 interior + 6 exterior (KHR punctual).

## LOD recommendations
LOD0 0-110 m, LOD1 110-300 m, LOD2 300-1800 m (glTF node extras `visibility_range_*`, applied by
`../../premium_commercial_17/premium_lod_post_import.gd`). The glass facade and main entrance remain in every LOD. For Unreal
Engine 5, import LOD0 (Nanite-friendly) and use LOD1/LOD2 as HLOD inputs, with glass set to Translucent.

## Modular collections
`SIDEWALK_FRONTAGE` (promenade stone-paving strip, removable), `OPTIONAL_FORECOURT` (terrace + street furniture + empty planters: Four timber terrace decks under the canopy (optional collection).), `SIGNAGE`,
`COLLISION` (`*-convcolonly` boxes, 2 pieces). There is no parking or vegetation.

## Validation (Blender only)
Result: **PASS**. The `.blend` was reopened in a fresh process, and the checks were:
mesh.validate, degenerate faces, winding, UVs, material slots, glass alpha < 1, LOD order and extras, missing textures, and vegetation. The GLB
was then exported, parsed with every embedded image decoded, and re-imported into a clean scene
(95,766 triangles, matching 95,766). Interior visibility was ray-traced from
the day and road cameras (see `renders/render_report.json`). **Godot import has NOT been tested.** Unreal import has not been tested.
