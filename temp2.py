from hex_map_functions import *
import h3

children = list(h3.h3_to_children("882aac889dfffff"))

m = visualize_hexagons(children)
for child in children:
    m = text_on_map(m,child,h3.h3_to_geo(child))

m.save("index.html")

