# Goal: Map showing score and shaded when n > tgt_density
# Find n for each hex on each res add to dict hex_dict -> (hex address: n) - done
# For each hotspot find and store hex address at res 10 through 4 - done
# In hspot_by_addr take lng,lat pass into h3_address - done
# save result as str in as new key:value pair in hspot_by_addr - done

# calculate tgt_density per hex
# add neighbors to hex_dict - done
# good_neighbors = neighbors at or above density_tgt
#


# Goal2: sandbox mode, add hotspots on the fly

from Hotspots import Hotspots
import h3

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

for hspot in h.hspot_by_addr:
    # try loop to skip all unasserted hspots
    for res in range(4, 11):
        try:
            h3_address = h3.geo_to_h3(h.hspot_by_addr[hspot]["lng"], h.hspot_by_addr[hspot]["lat"],
                                      res)  # lat, lng, hex resolution
            h.hspot_by_addr[hspot][f"res{res}_addr"] = h3_address
        except KeyError:
            continue

        try:
            hex_dict[res][h3_address]['n'] += 1
        except KeyError:
            hex_dict[res][h3_address] = {'n': 1}

del h3_address
del hspot
del res

for res in hex_dict:
    for hex in hex_dict[res]:
        hex_dict[res][hex]["neighbors"] = dict.fromkeys(h3.k_ring_distances(hex, 1)[1], "no")
        try:
            for neighbor in hex_dict[res][hex]["neighbors"]:
                if hex_dict[res][neighbor]['n'] > res_vars[res][1]:
                    hex_dict[res][hex][neighbor] = "yes"
        except KeyError:
            continue

print(h.hspot_by_addr["112UxrVuoSFUymU8HrqW8af9CoY5VkrJUfYDYuhnHiPsH7Lza9Lc"])
#print(hex_dict[8]["882aac8883fffff"])

