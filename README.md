# Olkusz area — interactive bus map

Interactive, poster-grade map of the buses of the **Olkusz commune union**
(Związek Komunalny Gmin „Komunikacja Międzygminna" w Olkuszu, ZKGKM): **28
lines / 1 853 km** across Olkusz, Bukowno, Bolesław, Klucze and Sławków, drawn
along the real street geometry.

## Live

**https://miqell24.github.io/olkusz-bus-map/** — GitHub Pages from `main:/docs`. Local build on port 8188 (`npm run serve`).

| what | detail |
|---|---|
| feed | `data.odt.org.pl/gtfs/olkusz-gtfs.zip` — ODT's copy, **the one with shapes** |
| lines | 457, 460–477 and 467A, plus the lettered ones: BP, G, M, PS, PSK, SŁ, WK, ZP, ZZ, Ż |
| stops | 560 poles |
| graph | OSM roadways, cut from the Geofabrik małopolskie and śląskie extracts |

**Two copies of this feed exist and they are not the same.** The union's own
export through kiedyPrzyjedzie (`api.odt.org.pl/feed/9/google_transit.zip`)
ships NO shapes; odt.org.pl republishes it WITH shapes — 25 154 points over the
same 28 routes and 1 333 trips. This map reads the ODT copy, and that alone
took the mean matching error from 6.3 m down to **1.1 m**. Neither copy carries
direction_id, so the headsign stays the direction key.

## Pipeline

`npm run download` fetches the feed, cuts the OSM and vendors MapLibre GL.
`npm run build` map-matches every line (HMM/Viterbi on the OSM graph) and
writes GeoJSON to `data/out/`; `npm run lines` adds the line-by-line view.
`npm run serve` hosts the map at http://localhost:8188.

Data: GTFS ZKGKM Olkusz (odt.org.pl) · base map © OpenFreeMap / OpenMapTiles /
OpenStreetMap contributors.
