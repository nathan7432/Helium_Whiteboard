# Goal: Map showing score and shaded when n > tgt_density
# Find n for each hex on each res add to dict hex_dict -> (hex address: n) - done
# For each hotspot find and store hex address at res 10 through 4 - done
# In hspot_by_addr take lng,lat pass into h3_address - done
# save result as str in as new key:value pair in hspot_by_addr - done

# calculate tgt_density per hex
# add neighbors to hex_dict - done
# good_neighbors = neighbors at or above density_tgt - done
# calc hex_density_limit and add to each hex in hex dict - done
# calc scaling factor per hotspot and add to hspot_by_addr - done

# Goal2: sandbox mode, add hotspots on the fly

from Hotspots import Hotspots
import h3
import numpy

def score():
    h = Hotspots()

    hex_dict = {}

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


    # add interactive field to hotspot
    # working 2/3/2021
    for hspot in h.hspot_by_addr:
        # if hspot == "11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke":
        #     print("p")
        if type(h.hspot_by_addr[hspot]["last_poc_challenge"]) == type(None):
            h.hspot_by_addr[hspot]["interactive"] = "no"
        elif h.hspot_by_addr[hspot]["last_poc_challenge"] > h.height - h.interacitve_var:
            h.hspot_by_addr[hspot]["interactive"] = "yes"
        else:
            h.hspot_by_addr[hspot]["interactive"] = "no"
    del hspot

    unasserted = 0  # incremented for every unasserted hspot

    # add field to hspot in hspot_by_addr and fill with its hex addresses 12 to 4
    # working 2/3/2021
    for hspot in h.hspot_by_addr:
        # try loop to skip all unasserted hspots
        # if hspot == "11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke":
        #     print("p")
        try:
            hex12_adr = h3.geo_to_h3(h.hspot_by_addr[hspot]["lat"], h.hspot_by_addr[hspot]["lng"], 12)
            h.hspot_by_addr[hspot]["hex_addr"] = hex_parents(hex12_adr)
            # temp = h.hspot_by_addr[hspot]["interactive"] #debug
            # int_temp_ty = print(type(h.hspot_by_addr[hspot]["interactive"])) #debug
            # int_temp_tp2 = type("yes") #debug
        except KeyError:
            unasserted += 1
    del hspot, hex12_adr

    # add hex and field n to hex_dict, number of interactive hotspots in hex
    # Working 2/3/2021
    for hspot in h.hspot_by_addr:
        if h.hspot_by_addr[hspot]["interactive"] == "yes":
            for hex in h.hspot_by_addr[hspot]["hex_addr"]:
                try:
                    hex_dict[hex]['n'] += 1
                except KeyError:
                    hex_dict[hex] = {'n': 1}
                    continue

    # add neighbors & children to hex in hex_dict
    # working 2/3/2021
    for hex in hex_dict:
        hex_dict[hex]["neighbors"] = dict.fromkeys(h3.k_ring_distances(hex, 1)[1], "no")
        # neighbor at density_tgt? yes/no
        for neighbor in hex_dict[hex]["neighbors"]:
            try:
                if hex_dict[neighbor]['n'] >= res_vars[h3.h3_get_resolution(neighbor)][1]:
                    hex_dict[hex]["neighbors"][neighbor] = "yes"
            except KeyError:
                continue
        hex_dict[hex]["children"] = h3.h3_to_children(hex)
    del hex, neighbor

    # sum good neighbors
    # working 2/3/2021
    for hex in hex_dict:
        temp_gd_neigh = 0
        for neighbor in hex_dict[hex]["neighbors"]:
            if hex_dict[hex]["neighbors"][neighbor] == "yes":
                temp_gd_neigh += 1
        hex_dict[hex]["good_neighbors"] = temp_gd_neigh
    del hex, neighbor, temp_gd_neigh

    # calculate density limit
    # working 2/3/2021
    for hex in hex_dict:
        res = h3.h3_get_resolution(hex)
        if (res < 11):
            # if hex == "882aac8883fffff":
            #     print("pause here")
            hex_dict[hex]["dens_lmt"] = min(res_vars[res][2], res_vars[res][1] * max(
                hex_dict[hex]["good_neighbors"] + 1 - res_vars[res][0] + 1, 1))
    del hex, res

    # hex sorted by resolution
    temp_hex_dict = {4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: []}
    for hex in hex_dict:
        res = h3.h3_get_resolution(hex)
        temp_hex_dict[res].append(hex)

    # testing clipping calc for res 10
    for hex in temp_hex_dict[10]:
        if hex == "892aac88817ffff":
            print("pause")
        hex_dict[hex]["unclipped"] = min(hex_dict[hex]["dens_lmt"] / hex_dict[hex]["n"], 1)
        hex_dict[hex]["clipped"] = min(hex_dict[hex]["dens_lmt"], hex_dict[hex]['n'])

    # sum clipped children
    # min(den limit/ sum clipped children, 1) = unclipped scaling
    for res in range(9, 3, -1):
        for hex in temp_hex_dict[res]:
            if hex == "892aac88817ffff": #debug
                print("pause") #debug
            temp_sum = 0
            for child in hex_dict[hex]["children"]:
                try:
                    temp_sum += hex_dict[child]["clipped"]
                except KeyError:
                    continue  # if child is not in hex_dict n = 0 and clipped is the min of n and density limit
            hex_dict[hex]["sum_clipped_children"] = temp_sum
            if temp_sum == 0:
                hex_dict[hex]["unclipped"] = 1
            else:
                hex_dict[hex]["unclipped"] = min(hex_dict[hex]["dens_lmt"] / temp_sum, 1)


    #
    # # calculate scaling factor for each hex
    # # this may not be needed anymore
    # for hex in hex_dict:
    #     res = h3.h3_get_resolution(hex)
    #     if (res < 11):
    #         hex_dict[hex]["scaling"] = min(hex_dict[hex]["dens_lmt"]/hex_dict[hex]["n"], 1)
    # del hex, res

    # calculate scaling factor per hotspot
    # broken
    for hspot in h.hspot_by_addr:
        # if hspot == "11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke": #debug
        #     print("pause") #debug
        first_loop = True
        try: #if unasserted next line will pass KeyError because it has no parent hex addresses
            for hex_adr in h.hspot_by_addr[hspot]["hex_addr"]:
                res = h3.h3_get_resolution(hex_adr)
                try:
                    if (res < 11):
                        if first_loop == True:
                            temp_scaling_list = []
                            temp_scaling_list.append(hex_dict[hex_adr]["unclipped"])
                            first_loop = False
                        else:
                            temp_scaling_list.append(hex_dict[hex_adr]["unclipped"])
                except KeyError:
                    continue
        except KeyError: # KeyError because it has no parent hex addresses, just continue
            continue
        temp_list = numpy.prod(temp_scaling_list)
        temp_var = h.hspot_by_addr[hspot]["reward_scale"] #debug
        h.hspot_by_addr[hspot]["tx_rwd_scaling"] = temp_list
    #
    #
    #
    #
    #
    #
    # # Testing purposes only
    # # TSA hex_8 = "882aac8883fffff"
    # # TSA addr = "11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke"
    # multiplier = hex_dict["882aac8883fffff"]["good_neighbors"] + 1 - res_vars[8][0] + 1
    # gn = hex_dict["882aac8883fffff"]["good_neighbors"]
    # scaling = h.hspot_by_addr["11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke"]["tx_rwd_scaling"] # for TMC
    # hex_dit_ex = hex_dict["882aac8883fffff"]
    # print(f"hex dict: {hex_dit_ex}")
    # print(f"Good neighbors: {gn}")
    # print(f"max: {res_vars[8][2]}")
    # print(f"tgt: {res_vars[8][1]}")
    # print(f"multiplier: {multiplier}")
    # print(hex_dict["882aac8883fffff"]["dens_lmt"])
    # print(hex_dict["882aac8883fffff"]["scaling"])
    # print(f"Transmit Reward Scaling: {scaling}")
    # print(f"Unasserted: {unasserted}")
    # del gn, multiplier, unasserted, scaling, hex_dit_ex
    #
    # TSA_hex_7 = "872aac888ffffff"
    # res = 7
    # # TSA addr = "11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke"
    # multiplier = hex_dict[TSA_hex_7]["good_neighbors"] + 1 - res_vars[res][0] + 1
    # gn = hex_dict[TSA_hex_7]["good_neighbors"]
    # scaling = h.hspot_by_addr["11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke"]["tx_rwd_scaling"] # for TMC
    # print(f"Hex dict: {hex_dict[TSA_hex_7]}")
    # print(f"Good neighbors: {gn}")
    # print(f"max: {res_vars[res][2]}")
    # print(f"tgt: {res_vars[res][1]}")
    # print(f"multiplier: {multiplier}")
    # print(hex_dict[TSA_hex_7]["dens_lmt"])
    # print(hex_dict[TSA_hex_7]["scaling"])
    # print(f"Transmit Reward Scaling: {scaling}")
    # del gn, multiplier, scaling, res, TSA_hex_7
    #
    no_match = 0
    unasserted_2 = 0

    # Checks calculated scaling vs API scaling
    # Make into fuction and send warning if this number is off when code is complete
    for hspot in h.hspot_by_addr:
        try:
            if (h.hspot_by_addr[hspot]["reward_scale"] != h.hspot_by_addr[hspot]["tx_rwd_scaling"]):
                no_match += 1
            API = h.hspot_by_addr[hspot]["reward_scale"] # debug
            my_score = h.hspot_by_addr[hspot]["tx_rwd_scaling"] # debug
            # if hspot == "11vB2aw3gWzoTPE6pN9LQmKGMBaVAkoq6AQ4jYHM1LEHpSCcSke": #debug
            # print(f"{hspot} : {API} : {my_score}") #debug
        except KeyError:
            unasserted_2 += 1
    print(f"no match: {no_match}")
    print(f"Unasserted 2: {unasserted_2}")

    return hex_dict
