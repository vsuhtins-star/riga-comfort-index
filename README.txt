Riga Comfort Index — prepared-data approach

This package changes the site so visitors load a static GeoJSON snapshot from the repository instead of querying Overpass directly when the page opens.

Files to upload to the repository, preserving paths:
- index.html
- scripts/build_comfort_data.py
- .github/workflows/update-comfort-data.yml

The GitHub Action runs on the first push of the workflow/script and then every Monday. It prepares data/comfort-features.geojson and commits it to main. You can also run it manually from GitHub → Actions → Refresh prepared comfort data → Run workflow.

The snapshot is sourced from OpenStreetMap contributors via Overpass. It includes mapped parks/green areas, public transport stops, schools/healthcare, and supermarkets/convenience shops/pharmacies. The website estimates proximity to feature points; it does not measure service quality, transit frequency, noise, or road traffic. Noise and major-road factors remain illustrative. Missing map features do not prove that a service is absent.

The existing riga_neighborhoods.geojson must remain in the repository root. Leaflet map tiles and address search still use their normal online services; the comfort-feature dataset itself is prebuilt and hosted by GitHub Pages.

OpenStreetMap attribution: © OpenStreetMap contributors (https://www.openstreetmap.org/copyright).
