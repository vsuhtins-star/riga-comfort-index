#!/usr/bin/env python3
"""Build a static GeoJSON snapshot of selected Riga amenities from OpenStreetMap.

This script runs occasionally (locally or in GitHub Actions), not in visitors'
browsers. Output format is consumed by index.html at data/comfort-features.geojson.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "comfort-features.geojson"
# Riga and its immediate urban area; Overpass bbox order is south, west, north, east.
BBOX = "(56.85,23.95,57.10,24.35)"
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

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

def categories(tags: dict) -> list[str]:
    result: list[str] = []
    if (
        tags.get("leisure") in {"park", "garden", "nature_reserve", "recreation_ground", "village_green"}
        or tags.get("landuse") == "forest"
        or tags.get("natural") in {"wood", "forest", "grassland"}
    ):
        result.append("green")
    if (
        tags.get("highway") == "bus_stop"
        or tags.get("public_transport") in {"platform", "stop_position", "station"}
        or tags.get("railway") in {"tram_stop", "station", "halt", "subway_entrance", "tram"}
        or tags.get("amenity") == "bus_station"
    ):
        result.append("transit")
    if (
        tags.get("amenity") in {"school", "kindergarten", "college", "university", "hospital", "clinic", "doctors", "dentist"}
        or bool(tags.get("healthcare"))
        or tags.get("building") in {"school", "kindergarten", "university", "hospital", "clinic"}
    ):
        result.append("schools")
    if tags.get("shop") in {"supermarket", "convenience", "pharmacy"} or tags.get("amenity") == "pharmacy":
        result.append("shops")
    return result

def get_coordinates(element: dict):
    # Nodes have lat/lon; ways and relations have a representative center from "out center".
    lat = element.get("lat")
    lon = element.get("lon")
    if lat is None or lon is None:
        center = element.get("center") or {}
        lat, lon = center.get("lat"), center.get("lon")
    if lat is None or lon is None:
        return None
    try:
        return float(lon), float(lat)
    except (TypeError, ValueError):
        return None

def fetch_snapshot() -> dict:
    body = urllib.parse.urlencode({"data": QUERY}).encode("utf-8")
    last_error = None
    for endpoint in ENDPOINTS:
        for attempt in range(2):
            try:
                request = urllib.request.Request(
                    endpoint,
                    data=body,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "User-Agent": "RigaComfortIndexDataBuilder/1.0 (static community project)",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(request, timeout=120) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload.get("elements"), list):
                    raise ValueError("Overpass response did not contain an elements list")
                return payload
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
                last_error = exc
                print(f"Request failed ({endpoint}, attempt {attempt + 1}): {exc}", file=sys.stderr)
                time.sleep(3 + attempt * 4)
    raise RuntimeError(f"All Overpass endpoints failed; existing dataset was not overwritten. Last error: {last_error}")

def main() -> int:
    print("Requesting one-time OpenStreetMap snapshot for Riga…")
    payload = fetch_snapshot()
    features = []
    seen = set()
    for item in payload["elements"]:
        tags = item.get("tags") or {}
        cats = categories(tags)
        coords = get_coordinates(item)
        if not cats or coords is None:
            continue
        key = (item.get("type"), item.get("id"))
        if key in seen:
            continue
        seen.add(key)
        properties = {
            "categories": cats,
            "name": tags.get("name", ""),
            "osm_type": item.get("type", ""),
            "osm_id": item.get("id"),
            "tags": {k: tags[k] for k in ("amenity", "healthcare", "highway", "leisure", "landuse", "natural", "public_transport", "railway", "shop") if k in tags},
        }
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [coords[0], coords[1]]},
            "properties": properties,
        })

    if len(features) < 100:
        raise RuntimeError(
            f"Only {len(features)} features returned. This looks incomplete; refusing to replace the dataset."
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    dataset = {
        "type": "FeatureCollection",
        "properties": {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source": "OpenStreetMap contributors via public Overpass API",
            "bbox": [23.95, 56.85, 24.35, 57.10],
            "feature_count": len(features),
            "note": "Point locations/representative centers for proximity estimates; not a complete inventory or service-quality measure.",
        },
        "features": features,
    }
    temp = OUTPUT.with_suffix(".geojson.tmp")
    temp.write_text(json.dumps(dataset, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    temp.replace(OUTPUT)
    print(f"Wrote {len(features):,} features to {OUTPUT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
