# Starbucks drive-thru café (prototype 02)

`starbucks_drive_thru.glb` — Godot import file · `source/starbucks_drive_thru.blend` — editable source
(`source/` and `renders/` contain a `.gdignore`, so Godot imports only the `.glb`).

**Footprint:** plot 46 m (X) × 42 m (Y), origin at plot centre on finished ground, road side faces Blender −Y
(= Godot +Z). Building 20 × 11 m, 6.8 m tall.

**What is modelled (real geometry):**
- Travertine-clad box (procedural 1.2 × 0.6 m stack-bond panel texture with veining, pits and joints),
  upper volume overhanging a recessed full-width glass storefront with mullions and a framed double entrance door.
- Vertical travertine fin screen (LOD0: 21 bevelled fins) carrying the green siren roundel (textured, emissive) and
  `STARBUCKS` channel letters; `DRIVE / THRU` letters on the flush right-hand volume; roundels on both side walls.
- Champagne-metal pergola (5 posts, edge beams, slats perpendicular to the façade) over a raised paver terrace,
  6 tables with leather chairs, 3 house-green umbrellas, charcoal planters with shrubs and grasses, facade uplights.
- Drive-thru running **clockwise** (UAE: driver on the left): entry gantry with `2.70 CLEARANCE` bar and a
  6 m vertical `STARBUCKS` column, menu board + order post on the rear lane, pickup window on the west wall
  (steel sill, green awning, `PICK-UP` sign, lit back-of-house), white vertical fin screen along the lane,
  lane lines, arrows and painted `DRIVE THRU`.
- Interior visible through the glass: wood-slat ceiling, pendant lights, bar counter with pastry case,
  three emissive menu boards on a house-green wall, indoor tables.
- 9 parking bays, landscaped beds with palms, 3 street lights.

**Note on the emblem:** the roundel is a simplified, stylised siren drawn procedurally for this prototype
(`source/textures/sbx_emblem_albedo.png`). Replace that PNG with official artwork if required; the disc UVs map the
full square image.

**Godot extras:** 12 `-convcolonly` collision boxes, 16 optional night lights. See `../README.md`.
