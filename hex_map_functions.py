import h3
import folium

# directly from example notebook
def visualize_hexagons(hexagons, color="red", folium_map=None):
    """
    hexagons is a list of hexcluster. Each hexcluster is a list of hexagons.
    eg. [[hex1, hex2], [hex3, hex4]]
    """
    polylines = []
    lat = []
    lng = []
    for hex in hexagons:
        polygons = h3.h3_set_to_multi_polygon([hex], geo_json=False)
        # flatten polygons into loops.
        outlines = [loop for polygon in polygons for loop in polygon]
        polyline = [outline + [outline[0]] for outline in outlines][0]
        lat.extend(map(lambda v: v[0], polyline))
        lng.extend(map(lambda v: v[1], polyline))
        polylines.append(polyline)

    if folium_map is None:
        m = folium.Map(location=[sum(lat) / len(lat), sum(lng) / len(lng)], zoom_start=13, tiles='cartodbpositron')
    else:
        m = folium_map
    for polyline in polylines:
        my_PolyLine = folium.PolyLine(locations=polyline, weight=8, color=color)
        m.add_child(my_PolyLine)
    return m

# pass in user input and creates 1 resolutions of hexes
def hex_map_res_x(resol, k_rings, center_point, color, m):  # pass in resolution, k_rings out, center_point, color
    h3_address = h3.geo_to_h3(center_point[0], center_point[1], resol)  # lat, lng, hex resolution
    for ring in range(k_rings, 1, -1):
        m = visualize_hexagons(list(h3.k_ring_distances(h3_address, k_rings)[ring-1]), color=color, folium_map=m)
        print("ring" + str(ring) + ":" + str(ring-1))
    m.save("index.html")