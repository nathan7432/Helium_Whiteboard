from Hotspots import Hotspots
import h3
import folium
from folium.plugins import FastMarkerCluster
import json
import time

h = Hotspots()


class Error(Exception):
    """Base class for other exceptions"""
    pass


class InputTooSmallError(Error):
    """Raised when the input value is too small"""
    pass


class InputTooLargeError(Error):
    """Raised when the input value is too large"""
    pass


class HexRangeError(Error):
    """Raised when hex range invalid"""
    pass


while True:
    try:
        map_center = [float(coord) for coord in input("Enter coordinates of interest in the following format: "
                                                      "Lat, Long\n").split(', ')]
        break
    except ValueError:
        print("Be sure to separate coords with a comma and space little guy...")
        time.sleep(2)
        print("\n")

while True:
    try:
        userHexRange = [int(userHex) for userHex in input("Enter hex range of interest in the following format: "
                                                          "smallest (10 or less), Biggest (4 or more)\n").split(', ')]
        if userHexRange[0] > 10:
            raise InputTooLargeError
        elif userHexRange[1] < 4:
            raise InputTooSmallError
        elif userHexRange[0] < userHexRange[1]:
            raise HexRangeError
        break
    except ValueError:
        print("Be sure to separate hex range with a comma and space little guy...")
        time.sleep(2)
        print("\n")
    except InputTooLargeError:
        print("Less than 10 dog...")
        time.sleep(2)
        print("\n")
    except InputTooSmallError:
        print("Greater than 4, plz fix")
        time.sleep(2)
        print("\n")
    except HexRangeError:
        print("Make first number bigger than second")
        time.sleep(2)
        print("\n")


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


k_rings_dict = {4: 2, 5: 4, 6: 8, 7: 10, 8: 18, 9: 24, 10: 34}  # temp until code built for user input, {resolution:k_rings}
color_dict = {10: "yellow", 9: "orange", 8: "red", 7: "blue", 6: "purple", 5: "green", 4: "black"}

# creates map to viz hexes on
m = folium.Map(location=[map_center[0], map_center[1]], zoom_start=9, tiles='cartodbpositron')

# visualizes all resolutions of hexes input by user
if userHexRange[0] == userHexRange[1]:
    hex_map_res_x(userHexRange[0], k_rings_dict.get(userHexRange[0]), map_center, color_dict.get(userHexRange[0]), m)
    print("hex map ran")

for res in range(userHexRange[0], userHexRange[1]-1, -1):
    hex_map_res_x(res, k_rings_dict.get(res), map_center, color_dict.get(res), m)
    print("res"+str(res))

# file: hotspots.json -> dict: hs_dict -> list: hotspots -> dict of hotspots

# open dict and save hotspots to a list
with open("hotspots.json", "r") as read_hs:
    json_dict = json.load(read_hs)
hs_list = json_dict["hotspots"]

# adds a point on the map for each hotspot
latlnglist = []
skipped = 1
for hs in range(0, len(hs_list)):
    try:
        latlnglist.append([hs_list[hs]["lat"], hs_list[hs]["lng"]])
    except KeyError:
        hs += 1
        skipped += 1

print(str(skipped) + " without Lat/Long")

m.add_child(FastMarkerCluster(latlnglist))
m.save("index.html")
