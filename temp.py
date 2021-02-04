import h3
from hex_map_functions import visualize_hexagons
from Hotspots import Hotspots

h = Hotspots()

hspot = h.hspot_by_addr["11VKaN7fEvDm6NaGhcZtNSU1KAQQmTSwuuJsYYEqzh8mSWkoEUd"]



from_google = [h3.geo_to_h3(hspot["lat"], hspot["lng"], 9)]

print(from_google)
m = visualize_hexagons(from_google)
m.save("index.html")
