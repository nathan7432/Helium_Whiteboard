from Score import score
from hex_map_functions import *

hexagons = list(h3.k_ring('882a100d6bfffff',3))
hex_dict = score()

m = visualize_hexagons_2(hexagons, hex_dict, folium_map=None)

# m = visualize_hexagons(hexagons, color="red", folium_map=None)
m.save('index3.html')