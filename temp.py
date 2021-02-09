import h3
from hex_map_functions import visualize_hexagons
from Hotspots import Hotspots
from folium.features import DivIcon
import folium
testList = []

h3_12 = h3.geo_to_h3(25.76004961592718, -80.19787993724776, 12)  # '8c2aac889cd6bff'
testList.append(h3_12)
h3_11 = h3.h3_to_parent(h3_12)  # '8b2aac889cd6fff'
testList.append(h3_11)
h3_10 = h3.h3_to_parent(h3_11)  # '8a2aac889cd7fff'
testList.append(h3_10)
h3_9 = h3.h3_to_parent(h3_10)  # '892aac889cfffff'
testList.append(h3_9)
h3_8 = h3.h3_to_parent(h3_9)  # '882aac889dfffff'
testList.append(h3_8)
h3_7 = h3.h3_to_parent(h3_8)  # '872aac889ffffff'
testList.append(h3_7)
h3_6 = h3.h3_to_parent(h3_7)
testList.append(h3_6)
h3_5 = h3.h3_to_parent(h3_6)
testList.append(h3_5)
h3_4 = h3.h3_to_parent(h3_5)
testList.append(h3_4)


