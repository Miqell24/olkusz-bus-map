#!/usr/bin/env bash
# Downloads input data: the GTFS feed, the OSM networks (Geofabrik + pyosmium)
# and MapLibre GL. Everything is cached — re-running only fetches what is
# missing.
#
# Olkusz: ONE feed, one operator — the commune union ZKGKM (Związek Komunalny
# Gmin „Komunikacja Międzygminna" w Olkuszu), whose buses serve Olkusz,
# Bukowno, Bolesław, Klucze and Sławków.
#
# TWO copies of that feed exist and they are NOT the same: the union's own
# export through kiedyPrzyjedzie (api.odt.org.pl/feed/9/google_transit.zip)
# ships NO shapes, while odt.org.pl republishes it WITH shapes (25 154 points)
# — same 28 routes, same 1 333 trips, but the corridors come from the publisher
# instead of being reconstructed from the stop sequence. This script takes the
# ODT copy for that reason. Neither carries direction_id, so the headsign is
# the direction key.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/gtfs data/osm web/vendor

# 1) GTFS — the city's bundle
if [ ! -f data/gtfs/routes.txt ]; then
  echo "== GTFS olkusz (odt.org.pl) =="
  curl -fL --retry 3 --max-time 600 \
    -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36" \
    -o data/gtfs.zip "https://data.odt.org.pl/gtfs/olkusz-gtfs.zip" -d data/gtfs
fi

# 2) OSM — from the Geofabrik małopolskie and śląskie extracts (the union
#    reaches past the voivodeship border), cut by pipeline/pbf-cut.py, which
#    needs `pip3 install --user osmium`. Overpass answered 504 on every mirror
#    the day this map was built, and a local cut is the same data anyway.
if [ ! -f data/osm/olkusz.json ]; then
  python3 -c "import osmium" 2>/dev/null || { echo "brak pakietu osmium — zainstaluj: pip3 install --user osmium" >&2; exit 1; }
  for V in malopolskie slaskie; do
    if [ ! -f "data/$V-latest.osm.pbf" ]; then
      echo "== Geofabrik $V-latest.osm.pbf =="
      curl -fL --retry 5 --retry-delay 5 -C - --max-time 3600 -o "data/$V-latest.osm.pbf"         "https://download.geofabrik.de/europe/poland/$V-latest.osm.pbf"
    fi
  done
  echo "== cutting OSM out of the extract =="
  python3 pipeline/pbf-cut.py
fi

# 3) MapLibre GL (vendored, no CDN at runtime)
if [ ! -f web/vendor/maplibre-gl.js ]; then
  echo "== MapLibre GL =="
  curl -fL --retry 3 -o web/vendor/maplibre-gl.js  https://unpkg.com/maplibre-gl@5.6.1/dist/maplibre-gl.js
  curl -fL --retry 3 -o web/vendor/maplibre-gl.css https://unpkg.com/maplibre-gl@5.6.1/dist/maplibre-gl.css
fi

echo "OK — data ready:"
du -sh data/gtfs data/osm/olkusz.json 2>/dev/null || true
