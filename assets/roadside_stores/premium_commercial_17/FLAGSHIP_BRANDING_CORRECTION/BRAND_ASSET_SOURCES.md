# Brand asset sources and provenance - seven flagship signage corrections

Retrieved 2026-11-04 from a cloud session. **Internal test-game assets only.** Nothing here implies any brand
partnership, dealership authorisation, sponsorship or endorsement. All marks remain the property of their owners
(see "Permissions needed before public / commercial distribution" at the end).

## How the artwork was obtained

The session's network policy blocks direct downloads from most brand websites. Three routes were used:

1. **Official websites through Firecrawl** (a page-retrieval service). The raw HTML of the live page was saved to disk and the
   logo's own inline SVG or embedded image was extracted programmatically (no hand transcription): apple.com,
   ford.com, mi.com and mercedes-benz.com.
2. **Porsche's own public design-system repository** (`github.com/porsche-design-system/porsche-design-system`, commit
   `0cb963fea33b343e6e78ba0ea09ba010ab4cadad`, 2026-11-03), read anonymously over git.
3. **simple-icons** (npm `simple-icons` 16.36.0, and 5.0.0 for the Mercedes star, which was removed from later versions).
   This is a curated collection of brand SVGs. Each icon records the official page it was taken from. The CC0 licence covers
   only the packaging; **the trademarks themselves are not CC0**.

The untouched downloads are in `source_vectors/original/`. The normalised layered SVGs that the build reads are in
`source_vectors/final/`, and the vector renders (PNG) used for flat cards and LOD2 are in `textures/`.
`_tools/build_logo_library.py` regenerates all of these. **No logo outline was drawn by hand or by AI.** The only work
done here was colour layering for physical signs, plus two recreations, both marked below.

| Brand | Mark used on the sign | Exact source | Provenance class |
|---|---|---|---|
| Mercedes-Benz | Three-pointed star in ring | simple-icons 5.0.0 `mercedes.svg` (its recorded source: https://www.mercedes-benz.com/) | Official-sourced vector |
| Mercedes-Benz | "Mercedes-Benz" wordmark | Logo image embedded in the footer of https://www.mercedes-benz.com/en/ (`brandhub-footer-sitemap__logo`, 1792 x 224 px PNG with alpha). Vectorised 1:1 with potrace (potracer 0.0.4, 3x supersampled, threshold 0.5). No glyph was redrawn. | Official raster, traced to vector |
| BMW | Roundel (letters, ring radii, quarter radius) | simple-icons 16.36.0 `bmw.svg` (source https://bmw.com). The bmw.com page (redirected to bmwusa.com) also lists the official `BMW_Grey_Logo.svg`. | Official-sourced vector + composed colours |
| Porsche | PORSCHE wordmark | Porsche Design System `packages/components/src/components/wordmark/wordmark.tsx` (`viewBox 0 0 4500 300`). The path was copied byte-for-byte. | **Official vector** |
| Porsche | Crest | Shape and line-art from simple-icons `porsche.svg` (source https://www.porsche.com). Colour regions come from the official modernised crest image in the same Porsche Design System repo (`packages/assets/projects/crest/src/porsche-crest@3x.png`, only 90 x 120 px). | **Recreation**: official-sourced vector, coloured from the official raster |
| Ford | Blue Oval with script | ford.com global navigation SVG symbol `navigation-menu-ford-logo` (`viewBox 0 0 80 30`). Paths and fills unchanged: oval `#00095B`, script and rim white. | **Official vector** |
| Samsung | SAMSUNG wordmark | simple-icons 16.36.0 `samsung.svg` (source and guidelines https://www.samsung.com/us/about-us/brand-identity/logo/). Samsung Blue `#1428A0`. | Official-sourced vector |
| Apple | Apple logo | apple.com global navigation SVG (`globalnav-link-apple`, https://www.apple.com/ae/). Path unchanged. | **Official vector** |
| Xiaomi | MI symbol | Squircle path and `#ff6900` copied from the mi.com header logo SVG (https://www.mi.com/global/). "MI" letterform from simple-icons `xiaomi.svg` (source https://www.mi.com/global), scaled 112/24 into the same frame. | Official vector + official-sourced vector |
| Xiaomi | lowercase "xiaomi" wordmark | **Typeset** in MiSans Latin Demibold, Xiaomi's own typeface (npm `misans` 5.0.0 repackaging; official page https://hyperos.mi.com/font/en/about/). Glyph outlines converted with fontTools. | **Recreation**: typographic, not the official wordmark file |

### Colours used on the physical signs

| Brand | Values | Note |
|---|---|---|
| Mercedes-Benz | Face `#E6E8EA` (white acrylic, self-lit), returns chrome | Dealership star built in 3D: chrome ring plus six faceted pyramid facets (two alternating face materials so the facets read by day and at night) |
| BMW | Ring `#111214`, blue `#0066B1` (BMW blue as recorded by simple-icons), white `#FFFFFF`, rims chrome `#C3C7CB` | Physical dealership emblem colouring (black ring with white letters). The 2020 flat logo is the communication logo and is not used on the building |
| Porsche | Letters `#F2F2F2` (brushed aluminium, self-lit) on graphite. Crest: gold `#D49E4E`, red `#8C0A0A`, black `#121212`, rim `#E2BD78` | Crest colours sampled from the official 2023 crest raster |
| Ford | Blue `#00095B` (from ford.com), white `#FFFFFF` | |
| Samsung | Sign face white `#FFFFFF` | The reversed (white) version is used because the fascia is black. The library SVG keeps Samsung Blue `#1428A0` |
| Apple | `#F5F5F7` self-lit, steel returns | Logo only, with no name text, as in Apple stores. iPhone products remain visible inside |
| Xiaomi | Symbol `#FF6900` with white MI. Wordmark `#1D1D1F` letters with a self-lit (halo) back face | The wordmark is dark on the white facade |

### Supporting facade text (not logos)

The following supporting lines are rebuilt with the original build parameters in **Inter Display SemiBold**
(SIL Open Font License), a licensed substitute for the proprietary Ford Antenna and Samsung typefaces, which are not
available for legitimate use here:

- Ford: "SERVICE", "PARTS & SERVICE RECEPTION"
- Samsung: "EXPERIENCE STORE"

BMW's two small generic-font text lines ("BMW" under the pylon roundel and "BMW  FLAGSHIP") were removed rather than
re-set in a non-BMW typeface. Porsche's old red accent bar on the monolith was replaced by the crest and the official
wordmark.

### Official reference pages named in the brief

| Page | Status from this session |
|---|---|
| https://brand-design.mercedes-benz.com/ | Blocked by the egress policy (not consulted directly) |
| https://www.press.bmwgroup.com/global/article/detail/T0306305EN/... | Blocked (not consulted directly) |
| https://newsroom.porsche.com/en_PME/2023/company/porsche-modernised-crest-evolution-of-an-icon-32504.html | Read through Firecrawl: "Brushed precious metal, three-dimensional honeycomb structure, refreshed crest animal and more subtle gold colour" |
| https://newsroom.porsche.com/en_PME/images-videos.html | Not used (high-resolution official crest artwork is not downloadable without newsroom access) |
| https://performance.ford.com/...Mustang-Cup-Brand-Guidelines-2025.pdf | Returns **404** (it redirects to fordracing.com, and the file is gone). Ford Blue was taken from ford.com's own logo SVG instead |
| https://www.samsung.com/bd/about-us/brand-identity/ | Blocked (the simple-icons record points to Samsung's US brand-identity logo page) |
| https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html | Read through Firecrawl (see permissions below) |
| https://www.mi.com/global/about/ and https://hyperos.mi.com/font/en/about/ | mi.com/global home page read through Firecrawl. The font page is blocked |

## Known gaps (honest status)

- **Porsche crest:** the modernised 2023 crest has a brushed-metal frame, a 3D honeycomb in the red fields and a refined
  horse. The vector used here is the line-art crest (it includes the STUTTGART lettering) with flat colours. Its
  layout, stripe order, colours and silhouette match the 2023 crest, but those finishes are missing. Replace it with Porsche's
  official crest artwork (available to licensees through the Porsche newsroom / partner portals) before any release.
- **Mercedes-Benz wordmark:** traced from an official 1792 px raster, so the curve accuracy is limited to about 1/1800 of
  the wordmark width (under 7 mm on the 11 m rooftop sign). The licensed vector file from the Mercedes-Benz brand design
  portal should replace it.
- **xiaomi wordmark:** a typographic recreation in the official MiSans typeface, not Xiaomi's wordmark artwork file.
- **BMW blue:** `#0066B1` is the BMW blue recorded with the vector. Physical roundels vary by generation and lighting.

## Permissions needed before public / commercial distribution

None of these marks is licensed to this project. Before any public build, trailer, store page or commercial release:

- **Apple:** Apple's guidelines (read 2026-11-04) say: "You may not use the Apple Logo or any other Apple-owned graphic
  symbol, logo, or icon ... for any other purpose except pursuant to an express written trademark license from Apple".
  A written licence is required, or the Apple store must be replaced with a fictional brand.
- **Porsche:** the Porsche Design System assets licence grants use "solely to develop, test, and distribute software
  applications, websites, and interfaces on behalf of Porsche". A game made by a third party is outside that. Licensing
  through Porsche AG is required.
- **Mercedes-Benz, BMW, Ford, Samsung, Xiaomi:** trademark and logo use in a commercial game normally needs a licence from
  the brand owner (Mercedes-Benz Group AG, BMW AG, Ford Motor Company, Samsung Electronics, Xiaomi Corporation). Car
  brands typically license through dedicated licensing programmes.
- **MiSans:** Xiaomi's font licence allows free commercial use. Confirm the current terms at https://hyperos.mi.com/font/en/about/.
- **Inter:** SIL Open Font License 1.1 (no permission needed).
- Keep the provenance table above with the assets so that the legal review can see exactly which artwork is used.
