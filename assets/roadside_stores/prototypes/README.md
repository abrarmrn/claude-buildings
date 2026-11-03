# Dubai roadside store prototypes (3 of 20)

Quality-benchmark assets for the Downtown Dubai / E11 driving game (Godot 4.7.2, PC).
**Status: built in Blender and exported; awaiting manual Godot verification. The remaining 17 stores have not been started.**

| # | Asset | Godot file | Editable source |
|---|---|---|---|
| 01 | ENOC service station | `enoc/enoc_service_station.glb` | `enoc/source/enoc_service_station.blend` |
| 02 | Starbucks drive-thru café | `starbucks/starbucks_drive_thru.glb` | `starbucks/source/starbucks_drive_thru.blend` |
| 03 | ZOOM convenience store | `zoom/zoom_convenience_store.glb` | `zoom/source/zoom_convenience_store.blend` |

Measured triangle counts, materials, texture sizes, memory estimates, file sizes and export warnings:
[`MEASUREMENTS.md`](MEASUREMENTS.md) (machine-readable: `measurements.json`).

| Asset | LOD0 tris | LOD1 tris | LOD2 tris | Materials | .glb | .blend |
|---|---:|---:|---:|---:|---:|---:|
| enoc_service_station | 79,830 | 14,109 | 2,446 | 41 | 10.3 MiB | 2.0 MiB |
| starbucks_drive_thru | 36,357 | 10,687 | 2,360 | 34 | 9.8 MiB | 1.3 MiB |
| zoom_convenience_store | 45,455 | 10,086 | 1,672 | 33 | 8.4 MiB | 1.4 MiB |

.blend and .glb export succeeded for all three (exporter result `FINISHED`); the triangle counts in the `.glb` match Blender exactly.

## How these were made (and what was not done)

- Built procedurally with **Blender 4.5.15 LTS** (the official `bpy` module from PyPI) in a headless Linux cloud
  container. Every asset is rebuilt from the scripts in `_tools/` — nothing was hand-placed, so the remaining 17
  stores can reuse the same library, materials and conventions.
- Visual checks were done with **Cycles** renders in Blender (`*/renders/`).
- **Not done:** no Godot import or in-engine check. The PC test project
  (`Desktop/Dubai-Game-Godot-PC-Test`) was not reachable from the container, and running a downloaded Godot binary
  was blocked by the session's permission policy. The production project was never touched, and no APK was made.
- Because the PC test project could not be inspected, its existing asset conventions could not be copied. The
  conventions below are self-consistent and documented, so they can be adjusted in one place
  (`_tools/roadside_lib.py`) if your project uses different ones.

## Folder layout

```
assets/roadside_stores/prototypes/
  README.md                       this file
  MEASUREMENTS.md / measurements.json
  roadside_lod_post_import.gd     Godot EditorScenePostImport script (LOD visibility ranges, light group)
  _tools/                         build + render + measure scripts (.gdignore'd)
  <asset>/
    <asset>.glb                   the only file Godot should import
    README.md
    source/                       .blend + generated textures + build log  (.gdignore'd)
    renders/                      Cycles inspection renders                (.gdignore'd)
```

To use in the PC test project, copy the whole `prototypes/` folder to e.g.
`res://assets/roadside_stores/prototypes/`. The `.gdignore` files keep Godot from importing the `.blend`
files (which would otherwise need a Blender path configured), the source textures (already embedded in each
`.glb`) and the preview PNGs.

## Conventions (shared by all 20 stores)

- **Scale:** 1 unit = 1 m, real-world dimensions.
- **Orientation:** the road / customer front faces Blender **−Y**, which exports as glTF/Godot **+Z**
  (`Vector3.MODEL_FRONT`). The road runs along X in front of the plot.
- **Origin:** centre of the plot at finished ground level (top of the forecourt asphalt is y = 0 in Godot).
  Each plot has a 0.3 m skirt below ground so it can sit on uneven terrain.
- **Hierarchy (glTF nodes):**
  ```
  ENOC_ServiceStation            root (extras: asset_id, front axis, units)
    ENOC_LOD0 / _LOD1 / _LOD2    LOD groups (extras: lod_level, visibility_range_begin/end/margin)
      ENOC_LOD0_Canopy ...       one merged mesh per logical part, several material surfaces each
    ENOC_Collision               ENOC_COL_*-convcolonly boxes (Godot import hint)
    ENOC_NightLights             optional KHR_lights_punctual spot/omni lights (shadows off)
  ```
  Prefixes: `ENOC_`, `SBX_`, `ZOOM_`.
- **Materials** are shared by name across stores: `RS_*` = generic (asphalt, paver, concrete, travertine, gravel,
  wood, glass, metals, paints, foliage, light panels), `ENOC_*` / `SBX_*` / `ZOOM_*` = brand. In Godot you can
  extract them once (Import dock → *Extract Materials*) and reuse the same `.tres` files for all 20 stores.
- **Textures:** procedurally generated, tileable 1024² (512² for small ones) albedo / ORM (R = 1, G = roughness,
  B = metallic) / OpenGL-convention normal maps, JPEG q92 4:4:4 (brand graphics are PNG). UVs are world-space
  box-projected at real-world tile sizes, so materials stay continuous across meshes. Textures are embedded in each `.glb`.
- **Normals:** smooth shading with sharp edges above 40°, then face-area-weighted normals, so bevelled
  edges catch light without shading gradients across flat faces.
- **Emission:** signs, light panels, screens and backlit fascias use the glTF emissive colour + `KHR_materials_emissive_strength`
  (strength 0.3–8 in Blender units). Daylight readability was checked in the renders. Tune Godot's glow /
  `emission_energy_multiplier` to taste.
- **Glass:** alpha-blended (`alphaMode BLEND`, alpha 0.30, double-sided, roughness 0.03) so it works without
  transmission support. LOD2 swaps glass + interior for an opaque dark glass with a faint warm emission (`RS_GlassLOD`).

## LODs in Godot

Each `.glb` contains **three real, separately modelled LODs** (not decimated copies; see the wireframe renders):

- **LOD0** (0–60 m): bevels, full signage with chamfered channel letters, pump nozzles/hoses, furniture, interiors
  with product boxes, LED bezels, wheel stops, shrubs and grasses.
- **LOD1** (60–170 m): no bevels, simplified pumps, chairs and props; interiors reduced to shelf blocks with the
  product texture; lower-resolution text, fewer fins, slats and palm fronds.
- **LOD2** (170–900 m): silhouette shells, flat low-resolution brand text (branding is kept), opaque glass,
  no interior, furniture, markings or shrubs.

Godot does not read Blender LOD systems, so the LODs are exported as sibling node groups. To switch them:

1. Select a `.glb` in the FileSystem dock → **Import** dock → **Import Script** → `roadside_lod_post_import.gd` → **Reimport**.
2. The script sets `visibility_range_begin/end` (+ 6 m hysteresis margins) on every mesh under `*_LOD0/1/2`,
   using the ranges stored in each LOD node's glTF extras (falls back to the node-name suffix).
3. Godot's own automatic mesh LOD ("Generate LODs", on by default) can stay on. It only further simplifies each
   mesh within its range.

Without the script all three LODs are drawn on top of each other. The ranges are defined once in
`_tools/roadside_lib.py` (`LOD_RANGES`) and in the script's `DEFAULT_RANGES`.

## Collision and lights

- `*-convcolonly` meshes become `StaticBody3D` + convex `CollisionShape3D` on import (Godot node-name import hint)
  and are not drawn. They are simple boxes: ground pad (top at y = 0), buildings, canopies, columns, islands,
  totems, lamp posts.
- Night lights are optional. The post-import script puts them in the group `roadside_store_night_lights`.
  Their energy was converted by the glTF exporter (standard physical units) and **will likely need tuning** in Godot.
  Delete them if you prefer to light the cluster yourself. All lights have shadows off.

## Rebuilding / creating the next stores

```bash
python3.11 -m venv venv && venv/bin/pip install bpy==4.5.15 pillow numpy arabic-reshaper python-bidi
```

```bash
PY=$PWD/venv/bin/python assets/roadside_stores/prototypes/_tools/run_all.sh
```

`run_all.sh` rebuilds all three `.blend` + `.glb` files from scratch, writes `source/build_log.txt`, renders
`renders/` (Cycles CPU, about 10–15 min per asset; `NO_RENDER=1` to skip) and regenerates `MEASUREMENTS.md`.
Fonts used: Inter (Latin) and DejaVu Sans Bold (Arabic, shaped with `arabic-reshaper` + `python-bidi`).

## Known limitations

- **Not verified in Godot** (see above). Expected behaviour (collision hints, extras→metadata, emissive strength,
  alpha blending, light conversion) is based on Godot 4's documented glTF importer, not on a test import.
- Real-time lights in the `.glb` are tuned for the Cycles renders, not for Godot's light units.
- The Starbucks roundel is a simplified procedural siren, not the official artwork (swap the PNG to replace it).
  The ENOC roundel is a simplified green/red split disc.
- Glass uses alpha blending, so you may see transparency-sorting artefacts where two glass panes overlap from a
  grazing angle (only the ZOOM promo vinyl sits just in front of glass).
- No lightmap UV2 channel is authored; Godot can generate UV2 on import (*Meshes → Light Baking: Static Lightmaps*).
- Textures are generated procedurally: tileable and consistent, but less rich than scanned PBR sets.
  Asphalt/paver/concrete/travertine can be swapped by replacing the `*_albedo/orm/normal.jpg` files and rebuilding.
- The export log contains a benign glTF exporter warning per asset ("More than one shader node tex image used for
  a texture"). It is triggered by roughness and metallic both reading the same ORM image through one Separate Color
  node; the exported `metallicRoughnessTexture` is correct (checked in the `.glb` JSON).
- The plots include their own forecourt/parking surfaces and landscaping. Road connection to your E11 network
  (kerb cuts, lane tapers) is left to placement.
