import h3
import folium
from folium.features import DivIcon, GeoJson
import json
from geojson.feature import *

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
        my_PolyLine = folium.PolyLine(locations=polyline, weight=1, color=color,)
        m.add_child(my_PolyLine)
    return m

def hex_map_res_x(resol, map_center, m, list_h3_visualized = []):
    """

    :param resol: resolution of hexagons to add to map
    :param map_center: converted to h3 address and determines center hexagon of resolution
    :param m: map object to add hexagons to
    :return: list of h3 address of hexagons visualized
    """
    k_rings_dict = {4: 2, 5: 4, 6: 8, 7: 10, 8: 6, 9: 24,
                    10: 34}  # change this for more or less rings
    k_rings = k_rings_dict[resol]
    color_dict = {10: "yellow", 9: "orange", 8: "red", 7: "blue", 6: "purple", 5: "green", 4: "black"}

    h3_address = h3.geo_to_h3(map_center[0], map_center[1], resol)  # center hex address
    list_h3_visualized.append(h3_address)
    for ring in range(k_rings, 1, -1):
        temp_viz = h3.k_ring_distances(h3_address, k_rings)[ring-1]
        list_h3_visualized.extend(temp_viz)
        m = visualize_hexagons(temp_viz, color=color_dict[resol], folium_map=m)
    return [list_h3_visualized, m]

def hex_map_res_all(m, userHexRange, map_center):
    """

    :param m: map object to add hexes
    :param userHexRange: resolutions of hexes to display
    :param map_center: center hex to viz k-rings around
    :return: list visualized hexes and map object with hexes added
    """
    if userHexRange[0] == userHexRange[1]:
        output = hex_map_res_x(userHexRange[0], map_center, m)
        m = output[1]
        list_h3_visualized = output[0]
    else:
        for res in range(userHexRange[0], userHexRange[1] - 1, -1):
            output = hex_map_res_x(res, map_center, m)
            print(f"Res {res} hexes added")
            m = output[1]
            list_h3_visualized = output[0]
    return [list_h3_visualized, m]

def text_on_map(m,text,coords):
    """

    :param m: map object to add 'text' to
    :param text: added to map
    :param coords: location on map
    :return: map object with added text
    """
    folium.map.Marker(
        coords,
        icon=DivIcon(
            icon_size=(250,36),
            icon_anchor=(10,20),
            html='<div style="font-family:Courier New; font-size: 10pt">'
                    f'<b>{text}</b>'
                 '</div>'
            )
        ).add_to(m)
    return m

def hex_parents(hex):
    """

    :param hex: child hex of interest
    :return: list of parent hexes including original child hex
    """
    res = h3.h3_get_resolution(hex)
    hex_list = [hex]
    while res > 4:
        hex_list.append(h3.h3_to_parent(hex))
        hex = h3.h3_to_parent(hex)
        res -= 1
    return hex_list

def visualize_hexagons_2(hexagons, hex_dict, folium_map=None):

    # get the geometry of the hexagon and convert to geojson
    for hex in hexagons:
        try:
            hex_dict[h3.h3_get_resolution(hex)][hex]["geometry"] = {"type": "Polygon",
                      "coordinates": [h3.h3_to_geo_boundary(h=hex, geo_json=True)]
                      }
        except(KeyError):
            # TODO: create error handling for this that finds dens_lmt of hex not in hex_dict
            print("Hex not in hex_dict")
            hex_dict[h3.h3_get_resolution(hex)][hex] = {
                "geometry": {"type": "Polygon", "coordinates": [h3.h3_to_geo_boundary(h=hex, geo_json=True)]},
                "sum_clipped_children": 1,
                "dens_lmt": 2
            }



    # create map if none is passed in
    if folium_map is None:
        m = folium.Map(location=h3.h3_to_geo(hexagons[0]),
                          zoom_start=13,
                          tiles="cartodbpositron",
                          attr='''© <a href="http://www.openstreetmap.org/copyright">
                                  OpenStreetMap</a>contributors ©
                                  <a href="http://cartodb.com/attributions#basemaps">
                                  CartoDB</a>'''
                          )

    # create feature object for each hex to viz
    list_features = []
    for hex in hexagons:
        res = h3.h3_get_resolution(hex)
        feature = Feature(geometry=hex_dict[res][hex]["geometry"],
                          addr=hex,
                          sum_clipped_children=hex_dict[res][hex]["sum_clipped_children"],
                          dens_lmt=hex_dict[res][hex]["dens_lmt"]
                          )
        list_features.append(feature)

    feat_collection = FeatureCollection(list_features)
    geojson_result = json.dumps(feat_collection)

    GeoJson(
        geojson_result,
        style_function=lambda feature: {
            'fillColor': None,
            'color': ("red"
                      if feature['sum_clipped_children'] > feature['dens_lmt']
                      else ("yellow" if feature['sum_clipped_children'] == feature['dens_lmt'] else "black")
                      ),
            'weight': 2,
            'fillOpacity': (0.05
                            if feature['sum_clipped_children'] >= feature['dens_lmt']
                            else 0)
        },
    ).add_to(m)

    return m

