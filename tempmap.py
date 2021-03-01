from folium import Map, Marker, GeoJson
import h3
import json
import pandas as pd
from geojson.feature import *

max_res = 4

lat_centr_point = 43.600378
lon_centr_point = 1.445478
list_hex_res = []
list_hex_res_geom = []
list_res = range(0, max_res + 1)

for resolution in range(0, max_res + 1):
    # index the point in the H3 hexagon of given index resolution
    h = h3.geo_to_h3(lat = lat_centr_point,
                     lng = lon_centr_point,
                     resolution = resolution
                     )

    list_hex_res.append(h)
    # get the geometry of the hexagon and convert to geojson
    h_geom = {"type": "Polygon",
              "coordinates": [h3.h3_to_geo_boundary(h = h, geo_json = True)]
              }
    list_hex_res_geom.append(h_geom)

df_res_point = pd.DataFrame({"res": list_res,
                             "hex_id": list_hex_res,
                             "geometry": list_hex_res_geom
                             })
df_res_point["hex_id_binary"] = df_res_point["hex_id"].apply(
                                                lambda x: bin(int(x, 16))[2:])

pd.set_option('display.max_colwidth', 63)

map_example = Map(location = [43.600378, 1.445478],
                  zoom_start = 5.5,
                  tiles = "cartodbpositron",
                  attr = '''© <a href="http://www.openstreetmap.org/copyright">
                          OpenStreetMap</a>contributors ©
                          <a href="http://cartodb.com/attributions#basemaps">
                          CartoDB</a>'''
                  )

list_features = []
for i, row in df_res_point.iterrows():
    feature = Feature(geometry = row["geometry"],
                      id = row["hex_id"],
                      properties = {"resolution": int(row["res"])})
    list_features.append(feature)

feat_collection = FeatureCollection(list_features)
geojson_result = json.dumps(feat_collection)

GeoJson(
        geojson_result,
        style_function = lambda feature: {
            'fillColor': None,
            'color': ("green"
                      if feature['properties']['resolution'] % 2 == 0
                      else "red"
                      ),
            'weight': 2,
            'fillOpacity': 0.05
        },
        name = "Example"
    ).add_to(map_example)

map_example.save('index2.html')