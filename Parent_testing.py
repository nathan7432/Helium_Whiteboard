from hex_map_functions import visualize_hexagons
import h3
from Hotspots import Hotspots


def hex_parents(hex):
    """

    :param hex: child hex of interest
    :return: list of parent hexes including orignial child hex
    """
    res = h3.h3_get_resolution(hex)
    hex_list = [hex]
    while res > 4:
        hex_list.append(h3.h3_to_parent(hex))
        hex = h3.h3_to_parent(hex)
        res -= 1
    return hex_list

h = Hotspots()

hspot_addr = "11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke"
lat = h.hspot_by_addr[hspot_addr]["lat"]
lng = h.hspot_by_addr[hspot_addr]["lng"]

hex_12 = h3.geo_to_h3(lat, lng, 12)
print(f"hex_12 type: {type(hex_12)}")
hex_parents = hex_parents(hex_12)
print(hex_parents)

m = visualize_hexagons(hex_parents)
m.save("index.html")

