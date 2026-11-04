# Boulevard 5 - build report

Generated 2026-11-04T07:22Z from the files on disk (Blender 4.5.15 LTS via the `bpy` module, Cycles CPU + OIDN, headless Linux cloud container).

## Checkpoint

- Phase B: 01 Maison Levant, 02 Juniper House: complete
- Phase C: 03 Lune & Laurel Cafe: complete
- Phase D: 04 Galerie D'Or, 05 The Promenade Galleria: complete
- Phase E: combined streetscape: complete (4 renders)
- Phase F: validation + reports: complete

**5 / 5 assets built, 20 / 20 asset renders + 4 streetscape renders. Blender validation: PASS for all.**

## Summary (triangles read from the exported GLB files)

| # | Asset | Storeys | W x D x H (m) | LOD0 | LOD1 | LOD2 | GLB MB | .blend MB | Materials | Lights int/ext | Validation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | Maison Levant | 2 | 22.0 x 18.0 x 11.22 | 39,976 | 12,298 | 1,112 | 7.84 | 1.33 | 42 | 9/6 | PASS |
| 02 | Juniper House | 1 (+mezz.) | 30.0 x 20.0 x 9.7 | 66,840 | 18,102 | 1,452 | 9.61 | 2.05 | 39 | 8/6 | PASS |
| 03 | Lune & Laurel Cafe | 2 | 16.0 x 15.0 x 10.92 | 39,790 | 12,838 | 1,371 | 7.69 | 1.41 | 41 | 6/3 | PASS |
| 04 | Galerie D'Or | 2 | 26.0 x 22.0 x 11.85 | 44,564 | 18,556 | 1,420 | 9.07 | 1.54 | 51 | 12/5 | PASS |
| 05 | The Promenade Galleria | 3 | 34.0 x 30.0 x 18.6 | 52,412 | 18,848 | 2,149 | 8.79 | 1.65 | 51 | 17/4 | PASS |

## Architectural diversity

| # | Frontage | Storeys / height | Glass : stone (approx. design intent) | Rhythm | Entrance | Canopy | Upper floor / roof | Terrace |
|---|---|---|---|---|---|---|---|---|
| 01 | 22 m | 2 / 11.2 m | ~60:40 | 5 tall bays, 0.9 m deep piers, symmetric | central, 7 m tall, 3 m recess | 3.4 m deep blade over the entrance only | two-storey glass bays, solid attic with letters | raised deck (left) |
| 02 | 30 m | 1 tall + mezzanine / 9.7 m | ~80:20 | 3 m grid of slender travertine mullions, horizontal | three recessed bays (6 m centre) | 4.6 m deep, full length | stepped crown with bronze fin screen | four decks under the canopy |
| 03 | 16 m | 2 / 10.9 m | ~50:50 | vertical composition + curved glass corner | arched, recessed, left | balcony doubles as canopy | balcony, stepped parapet | small bistro deck |
| 04 | 26 m | 2 / 11.9 m | ~45:55 | four different boutique shopfronts | central recess under a bay window | none (fascias) | punched windows, bay window, fluted attic | none |
| 05 | 34 m | 3 / 18.6 m (towers) | ~70:30 | towers + arcade colonnade + curtain wall | 12 m x 15 m atrium portal | glass + bronze, 5 m deep | curtain wall with fins, tower crowns, skylight | none (arcade) |

Only low-level construction helpers are shared (`bv_core.py` on top of the read-only premium kit). Each building has its own script that defines its massing, plan, facade rhythm, entrance, interior and site.

## Validation (per asset, `NN_*/validation.json`)

Each asset went through these steps: the build was saved, reopened in a fresh Blender process, run through mesh.validate, degenerate-face, winding, UV and material-slot checks, and checked that glass alpha is below 1 with blend mode set. LOD counts were checked to decrease and their extras to be present. Dimensions were recorded. The GLB was exported, parsed with embedded images decoded, and re-imported into a clean scene with triangle totals compared. Four renders were made, and interior probe points were ray-traced from the day and road cameras (glass may be crossed, opaque geometry may not).

- 01 Maison Levant: PASS; re-import 57,326 = GLB 57,326 tris; 34 textures loaded; interior probes visible: road view 1/4, day view 1/4; warnings: none
- 02 Juniper House: PASS; re-import 95,766 = GLB 95,766 tris; 34 textures loaded; interior probes visible: road view 0/4, day view 2/4; warnings: none
- 03 Lune & Laurel Cafe: PASS; re-import 56,605 = GLB 56,605 tris; 31 textures loaded; interior probes visible: road view 2/3, day view 2/3; warnings: none
- 04 Galerie D'Or: PASS; re-import 65,640 = GLB 65,640 tris; 32 textures loaded; interior probes visible: road view 1/4, day view 1/4; warnings: none
- 05 The Promenade Galleria: PASS; re-import 74,437 = GLB 74,437 tris; 27 textures loaded; interior probes visible: road view 2/6, day view 1/6; warnings: none

## LOD recommendations

- LOD0 0-110 m, LOD1 110-300 m, LOD2 300-1800 m, 8 m hysteresis (glTF node extras; Godot: `../premium_commercial_17/premium_lod_post_import.gd`).
- The glass facade and main entrance remain in every LOD. LOD2 replaces interiors with emissive glow proxies behind the glass.
- Unreal Engine 5: use the `unreal/*_LOD0/1/2.fbx` files (or the GLB through the Interchange glTF importer). Glass should be Translucent with Surface Forward Shading. Use LOD0 with Nanite, or set up LOD1/2 as LOD groups.

## Combined streetscape

`combined_streetscape/boulevard_five_streetscape.blend`: the five assets were appended side by side (128 m of continuous frontage) on one promenade, with 4 renders. This is a presentation demonstration only. The order and adjacency are not real geographic placement.

## Known limitations

- **Godot import has NOT been tested**, and neither has Unreal import. The cloud session cannot reach the local `Dubai-Game-Godot` / `Dubai-Game-Godot-PC-Test` projects, which were not touched, and nothing was copied to the user's computer.
- Glass is alpha-blended (engine-friendly), not refractive.
- Kitchens and back-of-house areas are closed off by partitions and are not modelled.
- The tower slot windows on The Promenade Galleria are glazed panels on the stone cores, which are service and stair cores with no public interior behind them.
- People, vehicles and vegetation are not modelled (vegetation is excluded by request; planters are empty).
- The preview street, neighbouring stub buildings and sky are render-only (`_PREVIEW_NOT_EXPORTED`).
- Fictional business names and signage use the OFL fonts Cinzel and Cormorant Garamond (`_tools/fonts/FONTS_LICENSE.md`).

## Git

- Branch: `claude/flagship-brand-fixes-boulevard-5`. The final commit hash is given in the final report message.
