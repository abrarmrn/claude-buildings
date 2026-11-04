# The Promenade Galleria - Premium shopping and dining gallery (largest)

Boulevard podium asset 05 of 5 for a **Sheikh Mohammed bin Rashid Boulevard (Downtown Dubai)**-inspired street.
This is a fictional business for an internal test game: it is not a real shop, and no real tenant position or geographic
placement is implied. There is no vegetation (planters are empty).

## Architecture
Two limestone towers with bronze slot windows and crowns; 4 m deep stone-column arcade with shopfronts; bronze curtain walls with fins on two upper floors; a 12 m wide, 15 m high set-back glazed atrium portal with a bronze-and-glass canopy.

## Interior
Three commercial levels around a central atrium: criss-cross escalators, glass-balustraded balcony walkways, twelve glazed shop units with fixtures and lit name bands, atrium seating, chandelier rings, glazed skylight.

## Dimensions (metres, Z-up, front = -Y in Blender = +Z in glTF)
| Item | Value |
|---|---|
| Frontage x depth | 34.0 x 30.0 |
| Height (top of podium / crown) | 18.6 |
| Commercial storeys | 3 |
| Floor levels | 0.15, 5.6, 10.4 (roof slab 15.2) |
| Tower interface | rear plane y = 30.0, podium roof z = 16.38, interface top z = 18.78 (empty `B05_TOWER_INTERFACE`) |
| Origin | centre of the frontage line (building line), ground level; promenade strip at y < 0 |

## Files
| File | Size |
|---|---|
| `the_promenade_galleria.blend` | 1.65 MB (editable source; build script `../_tools/build_05_*.py`) |
| `the_promenade_galleria.glb` | 8.79 MB (Godot: all LODs, promenade + terrace pieces, lights, collision, embedded textures) |
| `lod/the_promenade_galleria_lod0/1/2.glb` | 3.02 / 1.21 / 0.2 MB (geometry only) |
| `unreal/the_promenade_galleria_LOD0/1/2.fbx` | 1.38 / 0.64 / 0.24 MB (Unreal; LOD0 includes `UCX_` collision; textures referenced relatively from `../textures`) |
| `textures/` | PBR maps (albedo / ORM / normal, 1024 px JPEG) |
| `renders/` | four Cycles renders, 1600x900 |
| `validation.json`, `lod/build_stats.json` | validation results / build statistics |

## Triangle counts (read from the exported GLB files)
| LOD | Triangles | Contents |
|---|---|---|
| LOD0 | 52,412 | full facade detail, interiors, furniture, signage (26,324 interior tris) |
| LOD1 | 18,848 | full shell + glass, slabs, stairs/escalators, simplified furniture (7,088 interior tris) |
| LOD2 | 2,149 | massing, coarse glazing, glow proxies, simplified signage |
| Full GLB total | 74,437 | incl. promenade, terrace pieces and collision boxes |

## Materials
51 materials. Stone: BV_Limestone / BV_Travertine / BV_Champagne / BV_BeigeStone (procedural large-format panels with
joints, roughness and normal maps); metal: BV_Bronze / BV_BronzeDark / BV_BlackFrame (metallic 1.0, roughness 0.3-0.35);
glass: BV_Glass / BV_GlassWarm (real alpha blend 0.11-0.12, double-sided, low tint, so the interiors stay visible). Lights:
17 interior + 4 exterior (KHR punctual).

## LOD recommendations
LOD0 0-110 m, LOD1 110-300 m, LOD2 300-1800 m (glTF node extras `visibility_range_*`, applied by
`../../premium_commercial_17/premium_lod_post_import.gd`). The glass facade and main entrance remain in every LOD. For Unreal
Engine 5, import LOD0 (Nanite-friendly) and use LOD1/LOD2 as HLOD inputs, with glass set to Translucent.

## Modular collections
`SIDEWALK_FRONTAGE` (promenade stone-paving strip, removable), `OPTIONAL_FORECOURT` (terrace + street furniture + empty planters: None - arcade paving, benches, bollards, empty planters.), `SIGNAGE`,
`COLLISION` (`*-convcolonly` boxes, 4 pieces). There is no parking or vegetation.

## Validation (Blender only)
Result: **PASS**. The `.blend` was reopened in a fresh process, and the checks were:
mesh.validate, degenerate faces, winding, UVs, material slots, glass alpha < 1, LOD order and extras, missing textures, and vegetation. The GLB
was then exported, parsed with every embedded image decoded, and re-imported into a clean scene
(74,437 triangles, matching 74,437). Interior visibility was ray-traced from
the day and road cameras (see `renders/render_report.json`). **Godot import has NOT been tested.** Unreal import has not been tested.
