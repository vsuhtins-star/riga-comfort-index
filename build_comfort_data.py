#!/usr/bin/env python3
"""Build a static GeoJSON snapshot of Riga comfort features from OpenStreetMap.
Run by GitHub Actions, not by website visitors. Uses only Python's standard library.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BBOX = "(56.85,23.95,57.10,24.35)"  # south,west,north,east; covers Riga and nearby edge areas
OUT = Path("comfort-features.geojson")
QUERY = f"""
[out:json][timeout:90];
(
  nwr["leisure"~"^(park|garden|nature_reserve|recreation_ground|village_green)$"]{BBOX};
  nwr["landuse"="forest"]{BBOX};
  nwr["natural"~"^(wood|forest|grassland)$"]{BBOX};
  nwr["highway"="bus_stop"]{BBOX};
  nwr["public_transport"~"^(platform|stop_position|station)$"]{BBOX};
  nwr["railway"~"^(tram_stop|station|halt|subway_entrance|tram)$"]{BBOX};
  nwr["amenity"~"^(bus_station|school|kindergarten|college|university|hospital|clinic|doctors|dentist|pharmacy)$"]{BBOX};
  nwr["healthcare"]{BBOX};
  nwr["building"~"^(school|kindergarten|university|hospital|clinic)$"]{BBOX};
  nwr["shop"~"^(supermarket|convenience|pharmacy)$"]{BBOX};
);
out center tags;
"""


def categories(tags):
    result = []
    if (tags.get("leisure") in {"park", "garden", "nature_reserve", "recreation_ground", "village_green"}
        or tags.get("landuse") == "forest"
        or tags.get("natural") in {"wood", "forest", "grassland"}):
        result.append("green")
    if (tags.get("highway") == "bus_stop"
        or tags.get("public_transport") in {"platform", "stop_position", "station"}
        or tags.get("railway") in {"tram_stop", "station", "halt", "subway_entrance", "tram"}
        or tags.get("amenity") == "bus_station"):
        result.append("transit")
    if (tags.get("amenity") in {"school", "kindergarten", "college", "university", "hospital", "clinic", "doctors", "dentist"}
        or bool(tags.get("healthcare"))
        or tags.get("building") in {"school", "kindergarten", "university", "hospital", "clinic"}):
        result.append("schools")
    if tags.get("shop") in {"supermarket", "convenience", "pharmacy"} or tags.get("amenity") == "pharmacy":
        result.append("shops")
    return result


def fetch(endpoint):
    request = urllib.request.Request(
        endpoint,
        data=urllib.parse.urlencode({"data": QUERY}).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                 "User-Agent": "RigaComfortIndex-data-builder/1.0 (static open-data snapshot)"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload.get("elements"), list):
        raise RuntimeError("Overpass response did not include an elements list")
    return payload["elements"]


def main():
    errors = []
    elements = None
    for endpoint in ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"):
        for attempt in range(2):
            try:
                print(f"Requesting OSM snapshot from {endpoint} (attempt {attempt + 1})")
                elements = fetch(endpoint)
                break
            except Exception as exc:
                errors.append(f"{endpoint}: {exc}")
                print(f"Endpoint failed: {exc}", file=sys.stderr)
                time.sleep(5 * (attempt + 1))
        if elements is not None:
            break
    if elements is None:
        raise RuntimeError("All Overpass endpoints failed; existing prepared dataset will not be overwritten. " + " | ".join(errors))

    features = []
    seen = set()
    for item in elements:
        tags = item.get("tags") or {}
        cats = categories(tags)
        center = item.get("center") or {}
        lat = item.get("lat", center.get("lat"))
        lon = item.get("lon", center.get("lon"))
        key = (item.get("type"), item.get("id"))
        if not cats or lat is None or lon is None or key in seen:
            continue
        seen.add(key)
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(lon), float(lat)]},
            "properties": {"osm_type": item.get("type"), "osm_id": item.get("id"),
                           "categories": cats, "name": tags.get("name", "")}
        })
    if len(features) < 100:
        raise RuntimeError(f"Only {len(features)} usable features returned; refusing to replace dataset with a suspiciously small snapshot")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    collection = {
        "type": "FeatureCollection",
        "properties": {"generated_at": datetime.now(timezone.utc).isoformat(),
                        "source": "OpenStreetMap contributors via Overpass API",
                        "bbox": [23.95, 56.85, 24.35, 57.10],
                        "feature_count": len(features),
                        "categories": ["green", "transit", "schools", "shops"]},
        "features": features,
    }
    OUT.write_text(json.dumps(collection, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Wrote {len(features)} mapped features to {OUT} ({OUT.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()
