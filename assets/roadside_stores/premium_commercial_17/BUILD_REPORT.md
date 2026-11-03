# Premium Commercial 17 - build report

Generated 2026-11-03T21:17:46Z from the files on disk (Blender 4.5.15 LTS via the `bpy` module, Cycles CPU + OpenImageDenoise, headless Linux cloud container).

## Checkpoint

- Batch A: 01 Mercedes-Benz Flagship Showroom (complete), 02 BMW Flagship Showroom (complete), 03 Porsche Flagship Showroom (complete), 04 Ford Showroom (complete)
- Batch B: 05 Samsung Flagship Experience Store (complete), 06 Apple Flagship Store (complete), 07 Xiaomi Flagship Store (complete), 08 Shirin Restaurant (complete)
- Batch C: 09 Saffron Courtyard (complete), 10 Ember & Olive (complete), 11 Pearl Terrace (complete), 12 Apex Auto Lab (complete), 13 HydroLux Auto Spa (remaining)
- Batch D: 14 Pitlane Performance (remaining), 15 Crescent Galleria (remaining), 16 Serein Cafe (remaining), 17 Aurelia Coffee House (remaining)

**12 / 17 assets complete.** Remaining: HydroLux Auto Spa, Pitlane Performance, Crescent Galleria, Serein Cafe, Aurelia Coffee House
Last successful asset: Apex Auto Lab

## Summary table (triangles read from the exported GLBs)

| # | Asset | Storeys | W x D x H (m) | LOD0 | LOD1 | LOD2 | Cars (tris) | GLB MB | Materials | Images | Lights int/ext | Validation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | Mercedes-Benz Flagship Showroom | 3 | 48.0 x 28.0 x 20.9 | 37,538 | 9,696 | 1,609 | 8 (17,632) | 8.55 | 58 | 25 | 12/4 | PASS |
| 02 | BMW Flagship Showroom | 2 | 44.8 x 25.0 x 14.6 | 25,424 | 7,418 | 1,302 | 7 (15,456) | 5.95 | 49 | 16 | 7/2 | PASS |
| 03 | Porsche Flagship Showroom | 3 | 33.0 x 28.0 x 15.2 | 21,046 | 6,326 | 1,238 | 6 (13,084) | 7.45 | 58 | 28 | 10/2 | PASS |
| 04 | Ford Showroom | 1 | 64.0 x 24.0 x 10.8 | 20,922 | 7,590 | 1,857 | 7 (15,428) | 5.5 | 59 | 16 | 7/2 | PASS |
| 05 | Samsung Flagship Experience Store | 2 | 35.2 x 22.6 x 12.6 | 13,208 | 4,736 | 1,039 | 0 (0) | 6.14 | 36 | 25 | 6/2 | PASS |
| 06 | Apple Flagship Store | 2 | 33.0 x 31.0 x 10.45 | 15,036 | 3,596 | 508 | 0 (0) | 3.89 | 23 | 14 | 7/1 | PASS |
| 07 | Xiaomi Flagship Store | 2 | 26.0 x 20.0 x 10.6 | 14,060 | 3,898 | 1,230 | 0 (0) | 4.73 | 37 | 16 | 5/1 | PASS |
| 08 | Shirin Restaurant | 1 (+ 2-storey-high entrance tower) | 46.0 x 16.0 x 11.2 | 47,881 | 12,291 | 1,068 | 0 (0) | 7.61 | 25 | 25 | 5/3 | PASS |
| 09 | Saffron Courtyard | 2 | 44.0 x 27.0 x 12.3 | 54,664 | 13,377 | 1,762 | 0 (0) | 7.66 | 30 | 22 | 5/2 | PASS |
| 10 | Ember & Olive | 1 (tall, gabled) | 40.0 x 18.0 x 9.1 | 30,732 | 7,094 | 1,037 | 0 (0) | 7.44 | 32 | 23 | 5/4 | PASS |
| 11 | Pearl Terrace | 2 | 34.0 x 22.0 x 10.65 | 39,494 | 9,633 | 1,287 | 0 (0) | 5.98 | 27 | 18 | 4/2 | PASS |
| 12 | Apex Auto Lab | 1 (+ lounge office mezzanine) | 32.0 x 22.0 x 9.4 | 16,274 | 6,414 | 911 | 4 (8,788) | 5.64 | 64 | 22 | 5/1 | PASS |
| 13 | HydroLux Auto Spa | - | - | - | - | - | - | - | - | - | - | pending |
| 14 | Pitlane Performance | - | - | - | - | - | - | - | - | - | - | pending |
| 15 | Crescent Galleria | - | - | - | - | - | - | - | - | - | - | pending |
| 16 | Serein Cafe | - | - | - | - | - | - | - | - | - | - | pending |
| 17 | Aurelia Coffee House | - | - | - | - | - | - | - | - | - | - | pending |

Totals over complete assets: LOD0 336,279 tris, LOD1 92,069, LOD2 14,848, placeholder cars 70,388; 32 placeholder cars; 48 renders + contact sheet + offline gallery.

## Architectural diversity (why these are not one generator with different colours)

| # | Massing / roof | Glass | Site arrangement |
|---|---|---|---|
| 01 | 16.2 | PC_Glass alpha 0.16 curtain wall | optional side lot, 11 bays (OPTIONAL_PARKING); left vehicle crossing to forecourt/showroom door; right side driveway to rear service yard |
| 02 | sweeping 11.8-14.6 m | curved faceted curtain wall, PC_Glass alpha 0.16 | optional rear lot, 34 bays (OPTIONAL_PARKING); left side driveway from the service road to the rear yard; vehicle delivery door in the right blade |
| 03 | 14.6 | frameless-look PC_GlassClear alpha 0.11 | none (direct pedestrian frontage); right side driveway from the service road to a glazed vehicle door; no front parking |
| 04 | sawtooth, eaves 7.8 m, ridges 10.3 m, portal 10.8 m | 36 m display glazing PC_Glass alpha 0.16 + north lights | optional left-side customer lot, 9 bays + access aisle (OPTIONAL_PARKING); direct service apron from the service road to delivery bay + 2 service doors; separate parking crossing on the left |
| 05 | 12.0 | two-storey PC_Glass front + recessed entrance portal | none - short drop-off lay-by in OPTIONAL_FORECOURT; in/out crossings to a 2.8 m drop-off lay-by along the frontage (service road side) |
| 06 | 10.45 | frameless PC_GlassClear alpha 0.11 with glass fins | none (pedestrian plaza only); pedestrian only - no vehicle access |
| 07 | 9.6 | full-height PC_Glass behind ~35 % modular panel cover | optional left side car park, 6 bays (OPTIONAL_PARKING); left crossing to the small side car park; corner pedestrian plaza |
| 08 | 7.2 | 10 arched PC_Glass windows + portal | optional right side, 5 bays (OPTIONAL_PARKING); terrace opens directly onto the pavement; separate right-hand crossing to optional parking |
| 09 | stacked upturned plates, top 12.3 m | GF bronze-framed PC_Glass band + L1 glass behind timber battens | none - compact drop-off lay-by (OPTIONAL_FORECOURT); in/out crossings to a drop-off lay-by in front of the courtyard |
| 10 | 4 gables, eaves 6.5 m, ridges 9.1 m | 4 x 9.3 m bay windows + glazed gables (PC_Glass) | optional angled side parking, 6 bays (OPTIONAL_PARKING); right crossing to angled side parking |
| 11 | 9.8 | rounded champagne-framed PC_GlassClear walls on both floors | none (front + side terraces beside the pavement); pedestrian; no vehicle access |
| 12 | 8.6 | glass sectional bay doors (PC_GlassBlue) + lounge PC_Glass box | none; 16 m wide road-facing crossing straight to three raised glass bay doors |
| 13 | translucent wave canopy 6.1-8.9 m over a 4.6 m tunnel | glass tunnel side wall + glass lounge | none (queue lane only); separate ENTRY (left) and EXIT (right) crossings; tunnel runs parallel to the road |
| 14 | barrel vault, eaves 7.0 m, crown 11.75 m | glass observation panels + glazed arched lunette + glass reception box | optional left customer parking, 6 bays (OPTIONAL_PARKING); 40 m wide workshop apron straight off the service road to four roller doors; separate parking crossing |
| 15 | 21.8 | 66 m concave crescent curtain wall PC_Glass alpha 0.16 + skylight | optional right-side surface car park, 32 bays (OPTIONAL_PARKING); pedestrian entrance plaza on the frontage; separate right crossing to the optional car park |
| 16 | 8.7 | full-height PC_GlassClear on both floors in a black steel frame | none (pavement terrace); pedestrian only |
| 17 | stepped: terrace 4.8 m, upper roof 9.8 m, crown 10.5 m | curved GF PC_GlassClear corner + raked upper lounge glass | none (roadside stone terrace); pedestrian only |

Every asset has its own build script (`_tools/build_NN_*.py`) that designs its own massing, plan, roof, entrance, interior layout and site arrangement; only low-level helpers (curtain walls, slabs, stairs, furniture, cars, materials) are shared from `_tools/pk_*.py`.

## Method and conventions

- Units metres, Z up, front facing Blender -Y (glTF / Godot +Z), origin at the centre of the plot frontage line (back of the 4 m public pavement) at ground level.
- The earlier libraries `prototypes/_tools/roadside_lib.py` and `additional_17/_tools/store_kit.py` are imported READ-ONLY (byte-code writing disabled, texture cache redirected to `premium_commercial_17/_tools/texcache/`); nothing in `prototypes/` or `additional_17/` was modified.
- Real transparent glass: single double-sided panes with an alpha-blended PBR material (`PC_Glass` alpha 0.16, `PC_GlassClear` 0.11, `PC_GlassRail` 0.14) - no opaque "fake interior" textures. Interiors are real geometry: slabs, ceilings, stairs, escalators, railings, counters, furniture, products, display cars.
- Lighting: important fixtures are real KHR punctual lights (interior points/spots, exterior washes); small fixtures are emissive materials. Interior lights are on in all renders (showroom/store lighting); exterior lights only at night.
- LODs: LOD0 full detail; LOD1 keeps the full shell, glass, slabs, stairs and simplified furniture silhouettes (no small products); LOD2 is the massing with coarse glazing, slabs and emissive interior-glow proxies. Placeholder cars are a separate node with their own 0-340 m range.
- Collision: simple `*-convcolonly` boxes per main volume (same convention as the earlier stores).
- Textures: shared procedural 1024 px PBR sets (limestone, granite, marble, terrazzo, oak, corrugated metal, pavers, + earlier concrete/travertine/asphalt/wood), one 1024x512 screen-content atlas shared by all displays, PNG logo decals with alpha. JPEG maps keep the GLBs small.

## Validation performed (per asset, see each `validation.json`)

1. Saved `.blend`, reopened in a fresh Python/Blender process. 2. `Mesh.validate()` on every mesh, degenerate faces counted. 3. Winding of every watertight piece checked. 4. Dimensions / bounds recorded. 5. Material slots checked (no empty slots). 6. Glass materials checked for alpha < 1 + blend mode. 7. UV layer present and finite. 8. Interior geometry triangle count per LOD. 9. Placeholder cars: separate objects, parented only to `<P>_PLACEHOLDER_CARS`, not shared, not inside LOD collections; building-only GLB verified to contain no car nodes. 10. LOD counts strictly decreasing and LOD extras present. 11-13. GLB exported, parsed (per-group triangles, embedded images decoded with Pillow) and re-imported into a clean scene (triangle totals compared). 14-16. Four renders + ray-traced visibility: from the road-view and day cameras, rays to sample points on every placeholder car and to interior probe points may pass glass but not opaque geometry.

- Crescent Galleria: probes on the front gallery of each of the 4 levels and on the escalators are traced from the day and road cameras (see its README).

- 01 Mercedes-Benz Flagship Showroom: PASS; road view: cars readable 6/8, probes 1/5; day view: cars 8/8, probes 5/5
- 02 BMW Flagship Showroom: PASS; road view: cars readable 5/7, probes 1/4; day view: cars 6/7, probes 1/4
- 03 Porsche Flagship Showroom: PASS; road view: cars readable 3/6, probes 1/4; day view: cars 5/6, probes 3/4
- 04 Ford Showroom: PASS; road view: cars readable 2/7, probes 0/3; day view: cars 4/7, probes 1/3
- 05 Samsung Flagship Experience Store: PASS; road view: cars readable 0/0, probes 1/4; day view: cars 0/0, probes 2/4
- 06 Apple Flagship Store: PASS; road view: cars readable 0/0, probes 2/4; day view: cars 0/0, probes 3/4
- 07 Xiaomi Flagship Store: PASS; road view: cars readable 0/0, probes 1/4; day view: cars 0/0, probes 2/4
- 08 Shirin Restaurant: PASS; road view: cars readable 0/0, probes 0/3; day view: cars 0/0, probes 0/3
- 09 Saffron Courtyard: PASS; road view: cars readable 0/0, probes 3/4; day view: cars 0/0, probes 3/4
- 10 Ember & Olive: PASS; road view: cars readable 0/0, probes 2/3; day view: cars 0/0, probes 3/3
- 11 Pearl Terrace: PASS; road view: cars readable 0/0, probes 1/3; day view: cars 0/0, probes 3/3
- 12 Apex Auto Lab: PASS; road view: cars readable 3/4, probes 0/4; day view: cars 3/4, probes 1/4

## LOD transition recommendations

- Default: LOD0 0-90 m, LOD1 90-260 m, LOD2 260-1600 m, 8 m hysteresis margin (glTF node extras, applied by `premium_lod_post_import.gd`). Crescent Galleria (large): 0-140 / 140-380 / 380-2000 m.
- Glass stays transparent in every LOD and LOD1 keeps slabs, stairs/escalators and furniture silhouettes, so the interior does not disappear at normal roadside distances; LOD2 swaps detailed interiors for emissive glow proxies behind the glass.
- Placeholder cars: 0-340 m (they are expected to be replaced by the game's own vehicles with their own LODs).
- For Unreal Engine 5, import the LOD0 node (or use Nanite on LOD0) and use LOD1/LOD2 as HLOD inputs; glass materials should be set to Translucent / Surface Forward Shading.

## Known limitations

- Godot import has NOT been tested: the cloud session cannot reach the local `Dubai-Game-Godot-PC-Test` project. Neither Godot project was touched.
- Brand marks (Mercedes-Benz, BMW, Porsche, Ford, Samsung, Apple, Xiaomi) are simplified generic recreations made from primitives / procedural images, not official artwork - replace with licensed assets before release. Restaurant, cafe, garage and mall brands are fictional.
- Placeholder cars are deliberately simple lofted silhouettes (body, glasshouse, wheels, lights) - not production vehicles.
- Glass is alpha-blended (engine friendly) rather than physically refractive; in the renders it reads slightly lighter than real low-iron glass.
- Rear service areas / kitchens / back-of-house spaces that cannot be seen from the street are blocked by partitions and not modelled in detail (intentional).
- Render environment (street, sand ground, sky) is a preview set in `_PREVIEW_NOT_EXPORTED` and is not part of the exported assets.
- No vegetation is modelled anywhere (planters are empty structures) as requested.
- Copying an asset folder into Godot: exclude the `.blend` file (Godot would try to import it); `textures/` and `renders/` contain `.gdignore`.

## Git

- Branch: `claude/dubai-premium-commercial-17` (based on `claude/dubai-17-store-assets`).
- Recent commits:
```
322d38f Premium Commercial 17 - 11_pearl_terrace validated and rendered (batch C)
3d8bc05 Premium Commercial 17 - 10_ember_and_olive validated and rendered (batch C)
714d3e0 Premium Commercial 17 - 09_saffron_courtyard validated and rendered (batch C)
83a6690 Premium Commercial 17 - Saffron Courtyard day render
389de49 Premium Commercial 17 - Saffron Courtyard validation (renders in progress)
eb2c52e Premium Commercial 17 - Xiaomi interior re-shot from ground floor (stair + both levels); Batch B complete
91d1e3a Premium Commercial 17 - 08_shirin_restaurant validated and rendered (batch B)
7e18bc5 Stop tracking verbose Cycles render logs (timings are kept in render_report.json)
```
