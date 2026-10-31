Riga Comfort Index — live OpenStreetMap update

Contents:
- index.html: complete replacement page

Install:
1. Download and unzip this archive.
2. In your GitHub repository, open index.html and replace its contents with this file (or upload this file to replace it).
3. Commit the change to the main branch.
4. Keep riga_neighborhoods.geojson in the repository root beside index.html.
5. Open the published site and hard-refresh it.

Data behavior:
- The page requests parks/woodland, transit stops, schools/healthcare, and everyday amenities from public OpenStreetMap Overpass endpoints.
- Successful data is cached in the browser for up to six hours.
- If live requests fail, the page uses cached data if available; otherwise those factors temporarily use illustrative values.
- Noise exposure and major-road exposure remain illustrative.
- Proximity is a rough distance estimate, not a measure of quality, safety, frequency, or completeness.
