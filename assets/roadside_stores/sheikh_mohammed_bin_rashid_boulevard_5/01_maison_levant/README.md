# Maison Levant - Premium Levantine fine-dining restaurant

Boulevard podium asset 01 of 5 for a **Sheikh Mohammed bin Rashid Boulevard (Downtown Dubai)**-inspired street.
This is a fictional business for an internal test game: it is not a real shop, and no real tenant position or geographic
placement is implied. There is no vegetation (planters are empty).

## Architecture
Symmetrical limestone frontage: five tall bays between 0.9 m stone piers; four two-storey bronze-framed glass bays and a 7 m recessed central entrance under a deep bronze blade canopy; attic band with bronze letters.

## Interior
Double-height dining hall with chandelier rings, reception counter, velvet banquettes and round tables; first-floor private dining gallery with a glass balustrade over the void; stone-and-bronze stair; mashrabiya feature wall.

## Dimensions (metres, Z-up, front = -Y in Blender = +Z in glTF)
| Item | Value |
|---|---|
| Frontage x depth | 22.0 x 18.0 |
| Height (top of podium / crown) | 11.22 |
| Commercial storeys | 2 |
| Floor levels | 0.15, 5.0 (roof slab 9.2) |
| Tower interface | rear plane y = 18.0, podium roof z = 11.22, interface top z = 12.52 (empty `B01_TOWER_INTERFACE`) |
| Origin | centre of the frontage line (building line), ground level; promenade strip at y < 0 |

## Files
| File | Size |
|---|---|
| `maison_levant.blend` | 1.33 MB (editable source; build script `../_tools/build_01_*.py`) |
| `maison_levant.glb` | 7.84 MB (Godot: all LODs, promenade + terrace pieces, lights, collision, embedded textures) |
| `lod/maison_levant_lod0/1/2.glb` | 1.97 / 0.78 / 0.1 MB (geometry only) |
| `unreal/maison_levant_LOD0/1/2.fbx` | 1.06 / 0.41 / 0.14 MB (Unreal; LOD0 includes `UCX_` collision; textures referenced relatively from `../textures`) |
| `textures/` | PBR maps (albedo / ORM / normal, 1024 px JPEG) |
| `renders/` | four Cycles renders, 1600x900 |
| `validation.json`, `lod/build_stats.json` | validation results / build statistics |

## Triangle counts (read from the exported GLB files)
| LOD | Triangles | Contents |
|---|---|---|
| LOD0 | 39,976 | full facade detail, interiors, furniture, signage (25,542 interior tris) |
| LOD1 | 12,298 | full shell + glass, slabs, stairs/escalators, simplified furniture (4,420 interior tris) |
| LOD2 | 1,112 | massing, coarse glazing, glow proxies, simplified signage |
| Full GLB total | 57,326 | incl. promenade, terrace pieces and collision boxes |

## Materials
42 materials. Stone: BV_Limestone / BV_Travertine / BV_Champagne / BV_BeigeStone (procedural large-format panels with
joints, roughness and normal maps); metal: BV_Bronze / BV_BronzeDark / BV_BlackFrame (metallic 1.0, roughness 0.3-0.35);
glass: BV_Glass / BV_GlassWarm (real alpha blend 0.11-0.12, double-sided, low tint, so the interiors stay visible). Lights:
9 interior + 6 exterior (KHR punctual).

## LOD recommendations
LOD0 0-110 m, LOD1 110-300 m, LOD2 300-1800 m (glTF node extras `visibility_range_*`, applied by
`../../premium_commercial_17/premium_lod_post_import.gd`). The glass facade and main entrance remain in every LOD. For Unreal
Engine 5, import LOD0 (Nanite-friendly) and use LOD1/LOD2 as HLOD inputs, with glass set to Translucent.

## Modular collections
`SIDEWALK_FRONTAGE` (promenade stone-paving strip, removable), `OPTIONAL_FORECOURT` (terrace + street furniture + empty planters: Raised timber dining terrace with parasols (optional collection).), `SIGNAGE`,
`COLLISION` (`*-convcolonly` boxes, 2 pieces). There is no parking or vegetation.

## Validation (Blender only)
Result: **PASS**. The `.blend` was reopened in a fresh process, and the checks were:
mesh.validate, degenerate faces, winding, UVs, material slots, glass alpha < 1, LOD order and extras, missing textures, and vegetation. The GLB
was then exported, parsed with every embedded image decoded, and re-imported into a clean scene
(57,326 triangles, matching 57,326). Interior visibility was ray-traced from
the day and road cameras (see `renders/render_report.json`). **Godot import has NOT been tested.** Unreal import has not been tested.
