# Additional 17 roadside store assets (Dubai Open World)

Seventeen original Blender-built commercial store assets (Blender 4.5.15 LTS) that follow the conventions of the three prototypes in `../prototypes/`
(1 unit = 1 m, road-facing front = Blender -Y = Godot +Z, origin at plot centre at ground, LOD0/1/2 nodes, `-convcolonly` collision boxes, night lights).

- **See the results without Blender:** open `STORE_CATALOG_17.html` (offline) or `STORE_CATALOG_17.jpg`; individual images are in `PREVIEW_GALLERY/` (4 per store: day, night, road view, detail).
- Per store folder: `<name>.blend`, `<name>.glb` (Godot import file), `lod/` (geometry-only LOD GLBs), `textures/`, `renders/`, `README.md`, `validation.json`.
- `STORE_ASSET_MANIFEST.json` - dimensions, measured triangle counts, file sizes, placement categories, validation results. `BUILD_REPORT.md` - what was verified and what was not.
- `roadside_lod_post_import.gd` - verbatim copy of the prototype Godot post-import script (assign as import script to enable LOD switching).
- `_tools/` - generator, validation, render and report scripts (rebuild any store with `build_NN_*.py`).

Godot import has **not** been tested (no access to the local project from the cloud session). Brand marks are simplified recreations, not official artwork.
