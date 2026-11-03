# ZOOM convenience store (prototype 03)

`zoom_convenience_store.glb` — Godot import file · `source/zoom_convenience_store.blend` — editable source
(`source/` and `renders/` contain a `.gdignore`, so Godot imports only the `.glb`).

**Footprint:** plot 42 m (X) × 34 m (Y), origin at plot centre on finished ground, road side faces Blender −Y
(= Godot +Z). Building 24 × 11 m, 6.4 m tall.

**What is modelled (real geometry):**
- White aluminium-composite box with the signature red **swoosh fascia** (extruded front-elevation profile with the
  sweeping right-hand tail, backlit at night), red piping line, band returns on both side elevations,
  white `ZOOM` and Arabic `زووم` channel letters (front) and `ZOOM` on both sides — the fascia sits above the
  entrance canopy so it stays readable from the road.
- 17 m full-height glass storefront with mullions, transom, automatic sliding-door header and red promo vinyl,
  red `services / خدمات` panel and a digital ad screen (both textured + emissive).
- 25 × 4 m entrance canopy at 3.8 m clearance with 20 downlights and 4 steel columns, galvanised bollards with red
  bands, LPG cylinder cage, ice merchandiser and bins (LOD0).
- Interior: 6 gondola runs with product boxes (8×8 packaging atlas), a full wall of lit coolers with bottle
  silhouettes, red brand band, ceiling light rows, red checkout counter with back display, hanging promo boards.
- 6.4 m ZOOM pylon (lit red head, `24/7`), 9 parking bays incl. accessible hatch, wheel stops, arrows,
  landscaped beds with palms, 4 street lights, rooftop HVAC.

**Godot extras:** 13 `-convcolonly` collision boxes, 11 optional night lights. See `../README.md`.
