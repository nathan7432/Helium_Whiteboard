from Score import score
from Hotspots import Hotspots
from hex_map_functions import *

hex_dict = score()
h = Hotspots()

def paraDisplay(hotspot_address):
    lat = h.hspot_by_addr[hotspot_address]["lat"]
    lng = h.hspot_by_addr[hotspot_address]["lng"]
    res12 = h3.geo_to_h3(lat, lng, 12)
    parents = hex_parents(res12)
    parents = parents[2:]

    print(f"res hex density_lmt sum_clipped_children")
    for hex in parents:
        res = h3.h3_get_resolution(hex)
        dens_lmt = hex_dict[res][hex]["dens_lmt"]
        try:
            sum_clipped_children = hex_dict[res][hex]["sum_clipped_children"]
        except KeyError:
            if res != 10: print(f"KeyError on res {res}")
            sum_clipped_children = hex_dict[res][hex]['n']
        print(f"{res} {hex} {dens_lmt} {sum_clipped_children}")

    return

def main():
    paraDisplay("11RC68j9rdv6jAtHWg76bkkekXB5GRgjoiXjRT9mxp9AoxaT9SJ")
    return

main()
