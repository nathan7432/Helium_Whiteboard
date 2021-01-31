import h3
from hex_map_functions import visualize_hexagons




from_google = [h3.geo_to_h3(40.08421106420869, -75.70324028092018, 8)]
from_dict = ["882aac8881fffff"]

print(from_google)
m = visualize_hexagons(from_google)
m = visualize_hexagons(from_dict, color="green", folium_map=m)
m.save("index.html")

s = " "
print(h3.h3_to_geo(s.join(from_dict)))
