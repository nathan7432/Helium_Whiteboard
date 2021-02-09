# shade hexes based on ratio of n to lmt density


from Hotspots import Hotspots
import h3
import folium
from folium.plugins import FastMarkerCluster
import json
import time
from hex_map_functions import *
from Score import score

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


hex_dict = score()

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

# creates map to viz hexes on
m = folium.Map(location=[map_center[0], map_center[1]], zoom_start=13, tiles='cartodbpositron')

# add hexagons to map
output = hex_map_res_all(m,userHexRange,map_center)
output[1].save("index.html")
list_h3_visualized = output[0]

for hex in list_h3_visualized:
    try:
        text = hex_dict[hex]["clipped"]/hex_dict[hex]["unclipped"]
        if text != 1:
            text = str(hex_dict[hex]["clipped"])+"/"+str(hex_dict[hex]["unclipped"])
            m = text_on_map(m, text, h3.h3_to_geo(hex))
    except KeyError:
        continue
m.save("index.html")
# add test to each hex
# hexcoords = []
# for hex in hex_dict:
#
#     hexcoords.append([h3.h3_to_geo(hex)])
#     text_on_map(m,"test",hexcoords).save("index.html")

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