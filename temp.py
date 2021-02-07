import h3
from hex_map_functions import visualize_hexagons
from Hotspots import Hotspots
from folium.features import DivIcon
import folium

# h3_12 = h3.geo_to_h3(40.093490,-75.704068,12) # '8c2aac888172dff'
# h3_11 = h3.h3_to_parent(h3_12) # '8b2aac888172fff'
# h3_10 = h3.h3_to_parent(h3_11) # '8a2aac888177fff'
# h3_9 = h3.h3_to_parent(h3_10) # '892aac88817ffff'
# h3_8 = h3.h3_to_parent(h3_9) # '882aac8881fffff'

def hex_map_res_x(resol, center_point, m):
    """

    :param resol: resolution of hexagons to add to map
    :param center_point: converted to h3 address and determines center hexagon of resolution
    :param m: map object to add hexagons to
    :return: list of h3 address of hexagons visualized
    """
    k_rings_dict = {4: 2, 5: 4, 6: 8, 7: 10, 8: 6, 9: 24,
                    10: 34}  # change this for more or less rings
    k_rings = k_rings_dict[resol]
    color_dict = {10: "yellow", 9: "orange", 8: "red", 7: "blue", 6: "purple", 5: "green", 4: "black"}

    h3_address = h3.geo_to_h3(center_point[0], center_point[1], resol)  # center hex address
    list_h3_visualized = []
    for ring in range(k_rings, 1, -1):
        temp_viz = h3.k_ring_distances(h3_address, k_rings)[ring-1]
        list_h3_visualized.extend(temp_viz)
        m = visualize_hexagons(temp_viz, color=color_dict[resol], folium_map=m)
    return [list_h3_visualized, m]

