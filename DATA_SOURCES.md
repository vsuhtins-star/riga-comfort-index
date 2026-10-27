# Data integration checklist

Candidate sources:
- GEO RĪGA neighborhoods: https://georiga.eu/en/atvertie-dati/rigas-apkaimes/
- GEO RĪGA streets and addresses: https://georiga.eu/en/atvertie-dati/rigas-ielas-un-adreses/
- Latvian Open Data Portal: https://data.gov.lv/dati/eng/
- Rīgas satiksme open data: https://www.rigassatiksme.lv/en/about-us/publishable-information/open-data/
- OpenStreetMap: https://www.openstreetmap.org/

Before scoring with any layer:
1. Download source and record source URL, date, licence and attribution.
2. Inspect fields, coordinate reference system, geometry validity and completeness.
3. Transform to a metric CRS before calculating distances.
4. Generate the official 500 m grid and clip it to the Riga municipal boundary.
5. Link amenity features to grid cells using documented distance-decay functions.
6. Record per-cell data coverage and make missingness visible.
7. Validate outputs against known locations and avoid presenting estimates as official ratings.

The current prototype intentionally does not ingest these datasets and does not claim any score is real.
