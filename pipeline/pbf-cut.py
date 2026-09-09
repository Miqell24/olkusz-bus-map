#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cuts data/osm/olkusz.json (the roads) out of the Geofabrik malopolskie and
slaskie extracts — the same JSON shape Overpass returns
('elements': ways with tags, node ids and geometry), so build.mjs cannot tell
the difference.

The sheet is the agglomeration: the city and the zone lines the county
carriers run out to Trzebnica, Olesnica, Olawa, Sroda Slaska and Sobotka.
"""
import json, os, re, sys
import osmium

ROOT = os.path.join(os.path.dirname(__file__), '..')
PBFS = [os.path.join(ROOT, 'data', n) for n in
        ('malopolskie-latest.osm.pbf', 'slaskie-latest.osm.pbf')]
ROAD_BOX = (50.16, 19.33, 50.45, 19.74)   # S, W, N, E — every commune the union serves
RAIL_BOX = None           # no rails on this sheet
HW = re.compile(r'^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|service|busway|construction|motorway_link|trunk_link|primary_link|secondary_link|tertiary_link)$')
RAIL = re.compile(r'^(tram|light_rail|construction)$')

road_file = os.path.join(ROOT, 'data/osm/olkusz.json')
need_road, need_rail = not os.path.exists(road_file), False
print('drogi:', need_road, flush=True)
if not need_road:
    sys.exit(0)
os.makedirs(os.path.join(ROOT, 'data/osm'), exist_ok=True)
out_road, out_rail = [], []


class H(osmium.SimpleHandler):
    def way(self, w):
        tags = w.tags
        hw, rw = tags.get('highway'), tags.get('railway')
        is_road = need_road and hw is not None and HW.match(hw)
        is_rail = False
        if not is_road and not is_rail:
            return
        geom, ids = [], []
        la0, la1, lo0, lo1 = 90.0, -90.0, 180.0, -180.0
        for n in w.nodes:
            try:
                lo, la = n.lon, n.lat
            except osmium.InvalidLocationError:
                continue
            # node ids ride along: buildGraph() builds topology from el.nodes
            # and SILENTLY skips ways without them (the London t13 hole)
            ids.append(n.ref)
            geom.append({'lat': la, 'lon': lo})
            if la < la0: la0 = la
            if la > la1: la1 = la
            if lo < lo0: lo0 = lo
            if lo > lo1: lo1 = lo
        if len(geom) < 2:
            return
        el = {'type': 'way', 'id': w.id, 'nodes': ids, 'tags': {t.k: t.v for t in tags}, 'geometry': geom}
        if is_road and la1 >= ROAD_BOX[0] and la0 <= ROAD_BOX[2] and lo1 >= ROAD_BOX[1] and lo0 <= ROAD_BOX[3]:
            out_road.append(el)



for pbf in PBFS:
    if not os.path.exists(pbf):
        sys.exit(f'brak {pbf} — pobierz go (pipeline/download.sh)')
    print('czytam', os.path.basename(pbf), flush=True)
    H().apply_file(pbf, locations=True, idx='flex_mem')
GEN = 'pbf-cut.py (Geofabrik malopolskie + slaskie)'
if need_road:
    uniq, ids = [], set()
    for e in out_road:                # a way on the voivodeship border is in both
        if e['id'] in ids:
            continue
        ids.add(e['id'])
        uniq.append(e)
    out_road = uniq
    json.dump({'version': 0.6, 'generator': GEN, 'elements': out_road}, open(road_file, 'w'))
    print(f'drogi: {len(out_road)}', flush=True)

print('gotowe', flush=True)
