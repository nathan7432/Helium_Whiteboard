# Goal: Map showing score and shaded when n > tgt_density
# Find n for each hex on each res add to dict hex_dict -> (hex address: n) - done
# For each hotspot find and store hex address at res 10 through 4 - done
# In hspot_by_addr take lng,lat pass into h3_address - done
# save result as str in as new key:value pair in hspot_by_addr - done

# calculate tgt_density per hex
# add neighbors to hex_dict - done
# good_neighbors = neighbors at or above density_tgt - done
# calc hex_density_limit and add to each hex in hex dict - done
# calc scaling factor per hotspot and add to hspot_by_addr

# Goal2: sandbox mode, add hotspots on the fly

from Hotspots import Hotspots
import h3
import numpy

h = Hotspots()

hex_dict = {4: {}, 5: {}, 6: {}, 7: {}, 8: {}, 9: {}, 10: {}}

# resolution : [N, density_tgt, density_max]
res_vars = {
    4: [1, 250, 800],
    5: [1, 100, 400],
    6: [1, 25, 100],
    7: [2, 5, 20],
    8: [2, 1, 4],
    9: [2, 1, 2],
    10: [2, 1, 1],
}

unasserted = 0 # incremented for every unasserted hspot

for hspot in h.hspot_by_addr:
    # try loop to skip all unasserted hspots
    try:
        for res in range(4, 11):
            h3_address = h3.geo_to_h3(h.hspot_by_addr[hspot]["lat"], h.hspot_by_addr[hspot]["lng"], res)  # lat, lng, hex resolution
            if res == 4:
                h.hspot_by_addr[hspot]["hex_addr"] = []
                h.hspot_by_addr[hspot]["hex_addr"].append(h3_address)
            else:
                h.hspot_by_addr[hspot]["hex_addr"].append(h3_address)
            try:
                hex_dict[res][h3_address]['n'] += 1
            except KeyError:
                hex_dict[res][h3_address] = {'n': 1}
    except KeyError:
        unasserted += 1
        continue
del h3_address, hspot, res

for res in hex_dict:
    # add neighbors to hex_dict
    for hex in hex_dict[res]:
        hex_dict[res][hex]["neighbors"] = dict.fromkeys(h3.k_ring_distances(hex, 1)[1], "no")
            # neighbor at density_tgt? yes/no
        for neighbor in hex_dict[res][hex]["neighbors"]:
            try:
                if hex_dict[res][neighbor]['n'] >= res_vars[res][1]:
                    hex_dict[res][hex]["neighbors"][neighbor] = "yes"
            except KeyError:
                continue
del hex, neighbor, res

# sum good neighbors
for res in hex_dict:
    for hex in hex_dict[res]:
        temp_gd_neigh = 0
        for neighbor in hex_dict[res][hex]["neighbors"]:
            if hex_dict[res][hex]["neighbors"][neighbor] == "yes":
                temp_gd_neigh += 1
        hex_dict[res][hex]["good_neighbors"] = temp_gd_neigh
del hex, neighbor, res, temp_gd_neigh

# calculate density limit
for res in hex_dict:
    for hex in hex_dict[res]:
        if hex == "882aac8883fffff":
            print("pause here")
        hex_dict[res][hex]["dens_lmt"] = min(res_vars[res][2], res_vars[res][1] * max(hex_dict[res][hex]["good_neighbors"] + 1 - res_vars[res][0] + 1, 1))
del hex, res

# calculate scaling factor for each hex
for res in hex_dict:
    for hex in hex_dict[res]:
        hex_dict[res][hex]["scaling"] = min(hex_dict[res][hex]["dens_lmt"]/hex_dict[res][hex]["n"], 1)
del hex, res

# calculate scaling factor per hotspot
for hspot in h.hspot_by_addr:
    try:
        res = 4
        for hex_adr in h.hspot_by_addr[hspot]["hex_addr"]:
            if res == 4:
                temp_scaling_list = []
                temp_scaling_list.append(hex_dict[res][hex_adr]["scaling"])
            else:
                temp_scaling_list.append(hex_dict[res][hex_adr]["scaling"])
            res += 1
    except KeyError:
        continue
    h.hspot_by_addr[hspot]["tx_rwd_scaling"] = numpy.prod(temp_scaling_list)





# Testing purposes only
# TSA hex_8 = "882aac8883fffff"
# TSA addr = "11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke"
multiplier = hex_dict[8]["882aac8883fffff"]["good_neighbors"] + 1 - res_vars[8][0] + 1
gn = hex_dict[8]["882aac8883fffff"]["good_neighbors"]
scaling = h.hspot_by_addr["11VGQgdX25PLzPd6qNJ5ZQMZUV7HYGNAqz6QgSUKtMYqEbkcnDR"]["tx_rwd_scaling"] # for TMC
print(hex_dict[8]["882aac8883fffff"])
print(f"Good neighbors: {gn}")
print(f"max: {res_vars[8][2]}")
print(f"tgt: {res_vars[8][1]}")
print(f"multiplier: {multiplier}")
print(hex_dict[8]["882aac8883fffff"]["dens_lmt"])
print(hex_dict[8]["882aac8883fffff"]["scaling"])
print(f"Transmit Reward Scaling: {scaling}")
print(f"Unasserted: {unasserted}")
del gn, multiplier, unasserted, scaling