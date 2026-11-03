# ENOC service station (prototype 01)

`enoc_service_station.glb` — Godot import file · `source/enoc_service_station.blend` — editable source
(`source/` and `renders/` contain a `.gdignore`, so Godot imports only the `.glb`).

**Footprint:** plot 60 m (X) × 50 m (Y), origin at plot centre on finished ground (z = 0), road side faces Blender −Y
(= glTF/Godot +Z, `MODEL_FRONT`). Ground pad 0.3 m deep skirt below z = 0.

**What is modelled (real geometry):**
- 30 × 16 m canopy, 5.4 m clearance, rounded-corner fascia in ENOC green / red / white bands (backlit at night),
  charcoal brand panels front and back with the green/red roundel and lowercase `enoc` channel letters, Arabic
  `إينوك` on both side faces, white soffit with 18 recessed LED panels (bezels on LOD0).
- 4 pump islands (6.8 × 1.4 m, rounded, steel edge) with 8 double-sided dispensers: brushed-steel plinth and side
  rails, white cabinet, brand header, display + keypad, three colour-coded nozzles per side with holsters and
  hoses (LOD0), yellow crash hoops, bin and towel station.
- 4 canopy columns with ENOC price screens (textured, emissive) on three faces.
- 8.6 m price totem with roundel, wordmark, price LED panel (both faces) and Arabic name.
- 26 × 9 m shop (ZOOM, as at real ENOC sites): glass curtain wall with mullions/transom, sliding door,
  entrance overhang with downlights, green/red accent stripes, red ZOOM lightbox with Arabic `زووم`,
  rooftop HVAC; interior with lit ceiling strips, coolers, 4 stocked gondolas and a checkout counter.
- Paver forecourt, asphalt drives, 8 parking bays with wheel stops, zebra walkway, lane arrows,
  landscaped curb beds with palms/shrubs/grasses, 4 street lights.

**Godot extras:** 16 `-convcolonly` collision boxes (ground pad, canopy, islands, columns, shop, totem, lamp posts)
and 16 optional night lights (spot/omni, shadows off). See `../README.md` for the LOD setup.

Renders: `renders/` (day, night, drive-by, close-ups, LOD comparison, wireframe, LOD at switch distance).
Measurements: `../MEASUREMENTS.md`.
