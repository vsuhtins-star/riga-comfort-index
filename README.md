# Riga Comfort Index — prototype

A no-build static prototype of the Riga comfort-index interface.

## Run it
1. Unzip the project.
2. Open `index.html` in a modern browser. If the browser blocks external requests from `file://`, serve this folder locally:
   - Python: `python -m http.server 8000`
   - Open `http://localhost:8000`
3. Internet access is needed for the map tiles, Leaflet library and address search.

## Current features
- Interactive map centered on Riga
- Approximate 500 m grid overlay
- Selectable cells and score details
- Adjustable positive/negative factor weights and toggles
- Address/place search via public Nominatim
- Responsive sidebar and methodology caveat

## Important data status
This is an interface prototype, **not a validated comfort index**. Cell values are generated synthetically for testing the map, sliders and selection interactions. No official neighborhood boundaries, amenity inventory, transit timetable, noise data, or real comfort measurements are integrated yet. Grid is clipped to an approximate Riga viewing window, not the official city boundary. Do not publish or rely on its scores as real findings.

## External services / attribution
- Map tiles: OpenStreetMap contributors — https://www.openstreetmap.org/copyright
- Geocoding: Nominatim public service — https://operations.osmfoundation.org/policies/nominatim/
- Leaflet: https://leafletjs.com/
- Official candidate data: GEO RĪGA / Latvian Open Data Portal. Validate each dataset's current terms and fields before integration.

For a public production deployment, review all tile and geocoding service policies, usage limits, attribution and caching requirements. Consider self-hosted or policy-compliant alternatives if usage grows.
