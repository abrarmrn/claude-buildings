# Roadside store prototypes - measured results

All values below were measured by `_tools/measure.py` from the files on disk (Blender 4.5.15 LTS, `bpy` module). Triangle counts come from Blender loop triangles and are cross-checked against the index counts inside the exported `.glb`.

## Triangle counts per LOD

| Asset | LOD0 | LOD1 | LOD2 | LOD1 / LOD0 | LOD2 / LOD0 | GLB check (LOD0 / LOD1 / LOD2) |
|---|---:|---:|---:|---:|---:|---|
| enoc_service_station | 79,830 | 14,109 | 2,446 | 18% | 3.1% | 79,830 / 14,109 / 2,446 |
| starbucks_drive_thru | 36,357 | 10,687 | 2,360 | 29% | 6.5% | 36,357 / 10,687 / 2,360 |
| zoom_convenience_store | 45,455 | 10,086 | 1,672 | 22% | 3.7% | 45,455 / 10,086 / 1,672 |

Visibility ranges written into the LOD empties (glTF extras): LOD0: 0-60 m, LOD1: 60-170 m, LOD2: 170-900 m, margin 6 m.

## Files, materials, textures

| Asset | .glb size | .blend size | Materials (all LODs) | Textures | Texture memory, RGBA8 + mips | Est. VRAM-compressed + mips | Collision shapes | Night lights |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| enoc_service_station | 10.31 MiB | 2.03 MiB | 41 | 17 | 59.95 MiB | 9.85 MiB | 16 | 16 |
| starbucks_drive_thru | 9.80 MiB | 1.29 MiB | 34 | 20 | 79.94 MiB | 13.02 MiB | 12 | 16 |
| zoom_convenience_store | 8.44 MiB | 1.37 MiB | 33 | 15 | 57.63 MiB | 9.39 MiB | 13 | 11 |

Texture memory: "RGBA8 + mips" = width x height x 4 bytes x 4/3. "VRAM-compressed" assumes Godot's default desktop VRAM compression (BC1/DXT1 at 0.5 B/px for colour and ORM maps, BC5/RGTC at 1 B/px for normal maps) x 4/3 for mipmaps. This is an estimate from the formula, not a measurement inside Godot.

### enoc_service_station

- Materials per LOD: LOD0: 40, LOD1: 39, LOD2: 24
- Mesh objects per LOD: LOD0: 15, LOD1: 15, LOD2: 10
- GLB: 78 nodes, 56 meshes, 183 primitives (surfaces), 41 materials, 17 embedded images, 16 punctual lights
- glTF extensions used: KHR_materials_emissive_strength, KHR_materials_specular, KHR_lights_punctual
- Alpha-blended materials: RS_Glass; double-sided: RS_PalmFrond, RS_Glass
- Export warnings: `WARNING: More than one shader node tex image used for a texture. The resulting glTF sampler will behave like the first shader node tex image.`

| Texture | Size | File | RGBA8+mips | Est. VRAM+mips |
|---|---|---:|---:|---:|
| source/textures/asphalt_albedo.jpg | 1024x1024 | 243 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/asphalt_normal.jpg | 1024x1024 | 1543 KiB | 5.33 MiB | 1.33 MiB |
| source/textures/asphalt_orm.jpg | 1024x1024 | 427 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/concrete_albedo.jpg | 1024x1024 | 244 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/concrete_normal.jpg | 1024x1024 | 828 KiB | 5.33 MiB | 1.33 MiB |
| source/textures/concrete_orm.jpg | 1024x1024 | 293 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/enoc_price_albedo.png | 512x1024 | 54 KiB | 2.67 MiB | 0.33 MiB |
| source/textures/gravel_albedo.jpg | 512x512 | 73 KiB | 1.33 MiB | 0.17 MiB |
| source/textures/gravel_normal.jpg | 512x512 | 163 KiB | 1.33 MiB | 0.33 MiB |
| source/textures/gravel_orm.jpg | 512x512 | 61 KiB | 1.33 MiB | 0.17 MiB |
| source/textures/paver_albedo.jpg | 1024x1024 | 311 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/paver_normal.jpg | 1024x1024 | 847 KiB | 5.33 MiB | 1.33 MiB |
| source/textures/paver_orm.jpg | 1024x1024 | 410 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/products_albedo.png | 512x512 | 7 KiB | 1.33 MiB | 0.17 MiB |
| source/textures/wood_albedo.jpg | 512x512 | 65 KiB | 1.33 MiB | 0.17 MiB |
| source/textures/wood_normal.jpg | 512x512 | 75 KiB | 1.33 MiB | 0.33 MiB |
| source/textures/wood_orm.jpg | 512x512 | 75 KiB | 1.33 MiB | 0.17 MiB |

<details><summary>Per-object triangle counts</summary>

**LOD0**: Canopy 860, CanopyLights 568, Columns 1,024, Ground 310, Interior 15,520, LampPosts 1,120, Landscape 7,663, Markings 927, PriceTotem 466, PumpIslands 31,080, Roof 678, Signage 18,840, Store 484, StoreFrames 288, StoreGlass 2

**LOD1**: Canopy 356, CanopyLights 196, Columns 176, Ground 214, Interior 862, LampPosts 216, Landscape 2,040, Markings 79, PriceTotem 82, PumpIslands 2,632, Roof 30, Signage 6,932, Store 100, StoreFrames 192, StoreGlass 2

**LOD2**: Canopy 212, Columns 32, Ground 98, LampPosts 112, Landscape 390, PriceTotem 82, PumpIslands 216, Signage 1,202, Store 100, StoreGlass 2

</details>

### starbucks_drive_thru

- Materials per LOD: LOD0: 33, LOD1: 33, LOD2: 23
- Mesh objects per LOD: LOD0: 16, LOD1: 16, LOD2: 11
- GLB: 77 nodes, 55 meshes, 168 primitives (surfaces), 34 materials, 20 embedded images, 16 punctual lights
- glTF extensions used: KHR_materials_emissive_strength, KHR_materials_specular, KHR_lights_punctual
- Alpha-blended materials: RS_Glass; double-sided: RS_Glass, RS_PalmFrond, SBX_Umbrella
- Export warnings: `WARNING: More than one shader node tex image used for a texture. The resulting glTF sampler will behave like the first shader node tex image.`

| Texture | Size | File | RGBA8+mips | Est. VRAM+mips |
|---|---|---:|---:|---:|
| source/textures/asphalt_albedo.jpg | 1024x1024 | 243 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/asphalt_normal.jpg | 1024x1024 | 1543 KiB | 5.33 MiB | 1.33 MiB |
| source/textures/asphalt_orm.jpg | 1024x1024 | 427 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/concrete_albedo.jpg | 1024x1024 | 244 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/concrete_normal.jpg | 1024x1024 | 828 KiB | 5.33 MiB | 1.33 MiB |
| source/textures/concrete_orm.jpg | 1024x1024 | 293 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/gravel_albedo.jpg | 512x512 | 73 KiB | 1.33 MiB | 0.17 MiB |
| source/textures/gravel_normal.jpg | 512x512 | 163 KiB | 1.33 MiB | 0.33 MiB |
| source/textures/gravel_orm.jpg | 512x512 | 61 KiB | 1.33 MiB | 0.17 MiB |
| source/textures/paver_albedo.jpg | 1024x1024 | 311 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/paver_normal.jpg | 1024x1024 | 847 KiB | 5.33 MiB | 1.33 MiB |
| source/textures/paver_orm.jpg | 1024x1024 | 410 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/sbx_emblem_albedo.png | 1024x1024 | 110 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/sbx_menu_albedo.png | 512x1024 | 49 KiB | 2.67 MiB | 0.33 MiB |
| source/textures/travertine_albedo.jpg | 1024x1024 | 338 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/travertine_normal.jpg | 1024x1024 | 950 KiB | 5.33 MiB | 1.33 MiB |
| source/textures/travertine_orm.jpg | 1024x1024 | 463 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/wood_albedo.jpg | 512x512 | 65 KiB | 1.33 MiB | 0.17 MiB |
| source/textures/wood_normal.jpg | 512x512 | 75 KiB | 1.33 MiB | 0.33 MiB |
| source/textures/wood_orm.jpg | 512x512 | 75 KiB | 1.33 MiB | 0.17 MiB |

<details><summary>Per-object triangle counts</summary>

**LOD0**: Building 286, Fins 2,376, Frames 216, Gantry 760, Glass 4, Ground 354, Interior 3,478, LampPosts 840, Landscape 8,845, LaneScreen 222, Markings 175, PickupWindow 304, Roof 214, Signage 8,228, Terrace 9,705, Uplights 350

**LOD1**: Building 94, Fins 144, Frames 160, Gantry 88, Glass 4, Ground 258, Interior 710, LampPosts 162, Landscape 2,900, LaneScreen 122, Markings 175, PickupWindow 112, Roof 22, Signage 3,768, Terrace 1,716, Uplights 252

**LOD2**: Building 72, Fins 72, Gantry 76, Glass 4, Ground 146, LampPosts 84, Landscape 702, LaneScreen 72, PickupWindow 48, Signage 778, Terrace 306

</details>

### zoom_convenience_store

- Materials per LOD: LOD0: 32, LOD1: 29, LOD2: 19
- Mesh objects per LOD: LOD0: 12, LOD1: 12, LOD2: 8
- GLB: 62 nodes, 45 meshes, 144 primitives (surfaces), 33 materials, 15 embedded images, 11 punctual lights
- glTF extensions used: KHR_materials_emissive_strength, KHR_materials_specular, KHR_lights_punctual
- Alpha-blended materials: RS_Glass; double-sided: RS_Glass, RS_PalmFrond
- Export warnings: `WARNING: More than one shader node tex image used for a texture. The resulting glTF sampler will behave like the first shader node tex image.`

| Texture | Size | File | RGBA8+mips | Est. VRAM+mips |
|---|---|---:|---:|---:|
| source/textures/asphalt_albedo.jpg | 1024x1024 | 243 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/asphalt_normal.jpg | 1024x1024 | 1543 KiB | 5.33 MiB | 1.33 MiB |
| source/textures/asphalt_orm.jpg | 1024x1024 | 427 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/concrete_albedo.jpg | 1024x1024 | 244 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/concrete_normal.jpg | 1024x1024 | 828 KiB | 5.33 MiB | 1.33 MiB |
| source/textures/concrete_orm.jpg | 1024x1024 | 293 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/gravel_albedo.jpg | 512x512 | 73 KiB | 1.33 MiB | 0.17 MiB |
| source/textures/gravel_normal.jpg | 512x512 | 163 KiB | 1.33 MiB | 0.33 MiB |
| source/textures/gravel_orm.jpg | 512x512 | 61 KiB | 1.33 MiB | 0.17 MiB |
| source/textures/paver_albedo.jpg | 1024x1024 | 311 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/paver_normal.jpg | 1024x1024 | 847 KiB | 5.33 MiB | 1.33 MiB |
| source/textures/paver_orm.jpg | 1024x1024 | 410 KiB | 5.33 MiB | 0.67 MiB |
| source/textures/products_albedo.png | 512x512 | 7 KiB | 1.33 MiB | 0.17 MiB |
| source/textures/zoom_ad_albedo.png | 512x640 | 16 KiB | 1.67 MiB | 0.21 MiB |
| source/textures/zoom_services_albedo.png | 512x1024 | 14 KiB | 2.67 MiB | 0.33 MiB |

<details><summary>Per-object triangle counts</summary>

**LOD0**: Building 912, Canopy 2,868, CanopyLights 880, Frames 274, Glass 6, Ground 286, Interior 18,250, LampPosts 1,120, Landscape 7,237, Markings 1,004, Signage 12,296, Totem 322

**LOD1**: Building 208, Canopy 276, CanopyLights 400, Frames 178, Glass 6, Ground 190, Interior 1,324, LampPosts 216, Landscape 2,216, Markings 50, Signage 4,988, Totem 34

**LOD2**: Building 138, Canopy 56, Glass 2, Ground 94, LampPosts 112, Landscape 468, Signage 768, Totem 34

</details>
