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
import numpy
from hex_map_functions import *


h = Hotspots(True)

hex_dict = {4:{}, 5:{}, 6:{}, 7:{}, 8:{}, 9:{}, 10:{}, 11:{}, 12:{}}

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

hex_addr_key = {4: 8, 5: 7, 6: 6, 7: 5, 8: 4, 9: 3, 10: 2, 11: 1, 12: 0}

def hex_parents(hex):
    """

    :param hex: child hex of interest
    :return: list of parent hexes including original child hex
    """
    res = h3.h3_get_resolution(hex)
    hex_list = [hex]
    while res > 4:
        hex_list.append(h3.h3_to_parent(hex))
        hex = h3.h3_to_parent(hex)
        res -= 1
    return hex_list

def score():
    print("Running score")
    # add interactive field to hotspot
    interactive_counter_yes = 0
    interactive_counter_no = 0
    for hspot in h.hspot_by_addr:
        # if hspot == "11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke":
        #     print("p")
        if type(h.hspot_by_addr[hspot]["last_poc_challenge"]) == type(None):
            h.hspot_by_addr[hspot]["interactive"] = "no"
            interactive_counter_no += 1
        elif h.hspot_by_addr[hspot]["last_poc_challenge"] > h.last_cg - h.interacitve_var:
            h.hspot_by_addr[hspot]["interactive"] = "yes"
            interactive_counter_yes += 1
        else:
            h.hspot_by_addr[hspot]["interactive"] = "no"
            interactive_counter_no += 1
    del hspot

    unasserted = 0  # incremented for every unasserted hspot

    # add field to hspot in hspot_by_addr and fill with its hex addresses 12 to 4
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
    spot_in_list = hex_addr_key[10]
    for hspot in h.hspot_by_addr:
        if h.hspot_by_addr[hspot]["interactive"] == "yes":
            hex = h.hspot_by_addr[hspot]["hex_addr"][spot_in_list]
            # if hex == "8a2836ae864ffff":
                # print("pause")
            try:
                hex_dict[10][hex]["sum_clipped_children"] += 1
            except KeyError:
                hex_dict[10][hex] = {"sum_clipped_children": 1}
                continue

    temp = hex_dict[10]["8a2836ae864ffff"]["sum_clipped_children"]

    # add neighbors in hex_dict
    for hex in hex_dict[10]:
        hex_dict[10][hex]["neighbors"] = dict.fromkeys(h3.k_ring_distances(hex, 1)[1], "no")
        hex_dict[10][hex]["neighbors"][hex] = "no"  # Add for 11:19 test
        # neighbor at density_tgt? yes/no
        for neighbor in hex_dict[10][hex]["neighbors"]:
            try:
                if hex_dict[10][neighbor]["sum_clipped_children"] >= res_vars[h3.h3_get_resolution(neighbor)][1]:
                    hex_dict[10][hex]["neighbors"][neighbor] = "yes"
            except KeyError:
                continue
    del hex, neighbor

    # sum good neighbors
    for hex in hex_dict[10]:
        temp_gd_neigh = 0
        for neighbor in hex_dict[10][hex]["neighbors"]:
            if hex_dict[10][hex]["neighbors"][neighbor] == "yes":
                temp_gd_neigh += 1
        hex_dict[10][hex]["good_neighbors"] = temp_gd_neigh
    del hex, neighbor, temp_gd_neigh

    # calculate density limit
    for hex in hex_dict[10]:
        res = h3.h3_get_resolution(hex)
        # if hex == "892aac88817ffff":
        #     print("pause here")
        # temp_dl = min(res_vars[res][2],
        #                 res_vars[res][1] * max(hex_dict[hex]["good_neighbors"] + 1 - res_vars[res][0] + 1, 1))
        # density_lmt is the min of density_max and density_tgt * multiplier
        # multiplier is the max of
        hex_dict[10][hex]["dens_lmt"] = min(res_vars[res][2], res_vars[res][1] * max(
            hex_dict[10][hex]["good_neighbors"] - res_vars[res][0] + 1, 1))
        # OG test 11:19
        # hex_dict[hex]["dens_lmt"] = min(res_vars[res][2], res_vars[res][1] * max(
        #     hex_dict[hex]["good_neighbors"] + 1 - res_vars[res][0] + 1, 1))
    del hex, res

    # testing clipping calc for res 10
    for hex in hex_dict[10]:
        hex_dict[10][hex]["clipped"] = min(hex_dict[10][hex]["dens_lmt"], hex_dict[10][hex]["sum_clipped_children"])
        hex_dict[10][hex]["unclipped"] = min(hex_dict[10][hex]["dens_lmt"] / hex_dict[10][hex]["sum_clipped_children"], 1)



    ###################### res 10 done ###################################################3
    count = 0
    for res in range(9, 3, -1):

        # add hexes to hex_dict
        spot_in_list = hex_addr_key[res]
        for hspot in h.hspot_by_addr:
            if h.hspot_by_addr[hspot]["interactive"] == "yes":
                hex = h.hspot_by_addr[hspot]["hex_addr"][spot_in_list]
                if hex in hex_dict[res]:
                    continue
                else:
                    hex_dict[res][hex] = {}

        #add children
        for hex in hex_dict[res]:
            hex_dict[res][hex]["children"] = h3.h3_to_children(hex)

        # sum clipped children
        for hex in hex_dict[res]:
            # if hex in testList: #debug
                # print("pause") #debug
            temp_sum = 0
            res_view = h3.h3_get_resolution(hex) #debug
            for child in hex_dict[res][hex]["children"]:
                try:
                    temp_sum += hex_dict[res+1][child]["clipped"]
                except KeyError:
                    continue  # if child is not in hex_dict n = 0 and clipped is the min of n and density limit

            hex_dict[res][hex]["sum_clipped_children"] = temp_sum

        for hex in hex_dict[res]:
            hex_dict[res][hex]["neighbors"] = dict.fromkeys(h3.k_ring_distances(hex, 1)[1], "no")
            hex_dict[res][hex]["neighbors"][hex] = "no"  # Add for 11:19 test
            # neighbor at density_tgt? yes/no
            for neighbor in hex_dict[res][hex]["neighbors"]:
                try:
                    if hex_dict[res][neighbor]["sum_clipped_children"] >= res_vars[h3.h3_get_resolution(neighbor)][1]:
                        hex_dict[res][hex]["neighbors"][neighbor] = "yes"
                except KeyError:
                    continue
        del hex, neighbor

        # sum good neighbors
        for hex in hex_dict[res]:
            temp_gd_neigh = 0
            for neighbor in hex_dict[res][hex]["neighbors"]:
                if hex_dict[res][hex]["neighbors"][neighbor] == "yes":
                    temp_gd_neigh += 1
            hex_dict[res][hex]["good_neighbors"] = temp_gd_neigh
        del hex, neighbor, temp_gd_neigh

        # calculate density limit
        for hex in hex_dict[res]:
            res = h3.h3_get_resolution(hex)
            # if hex == "892aac88817ffff":
            #     print("pause here")
            # temp_dl = min(res_vars[res][2],
            #                 res_vars[res][1] * max(hex_dict[hex]["good_neighbors"] + 1 - res_vars[res][0] + 1, 1))
            # density_lmt is the min of density_max and density_tgt * multiplier
            # multiplier is the max of
            hex_dict[res][hex]["dens_lmt"] = min(res_vars[res][2], res_vars[res][1] * max(
                hex_dict[res][hex]["good_neighbors"] - res_vars[res][0] + 1, 1))
            # OG test 11:19
            # hex_dict[hex]["dens_lmt"] = min(res_vars[res][2], res_vars[res][1] * max(
            #     hex_dict[hex]["good_neighbors"] + 1 - res_vars[res][0] + 1, 1))
        del hex

        # testing clipping calc for res res
        for hex in hex_dict[res]:
            hex_dict[res][hex]["clipped"] = min(hex_dict[res][hex]["dens_lmt"], hex_dict[res][hex]["sum_clipped_children"])
            hex_dict[res][hex]["unclipped"] = min(hex_dict[res][hex]["dens_lmt"] / hex_dict[res][hex]["sum_clipped_children"],
                                                 1)


        # # hex sorted by resolution
        # temp_hex_dict = {4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: []}
        # for hex in hex_dict:
        #     res = h3.h3_get_resolution(hex)
        #     temp_hex_dict[res].append(hex)
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        # # sum clipped children
        # # min(den limit/ sum clipped children, 1) = unclipped scaling
        # for res in range(9, 3, -1):
        #     for hex in temp_hex_dict[res]:
        #         if hex in testList: #debug
        #             print("pause") #debug
        #         temp_sum = 0
        #         res_view = h3.h3_get_resolution(hex)
        #         for child in hex_dict[hex]["children"]:
        #             try:
        #                 temp_sum += hex_dict[child]["clipped"]
        #             except KeyError:
        #                 continue  # if child is not in hex_dict n = 0 and clipped is the min of n and density limit
        #         hex_dict[hex]["sum_clipped_children"] = temp_sum
        #         if temp_sum == 0:
        #             hex_dict[hex]["unclipped"] = 1
        #         else:
        #             unclipped = min(hex_dict[hex]["dens_lmt"] / hex_dict[hex]["sum_clipped_children"], 1)
        #             clipped = min(hex_dict[hex]["dens_lmt"], hex_dict[hex]["sum_clipped_children"])
        #             hex_dict[hex]["unclipped"] = min(hex_dict[hex]["dens_lmt"] / hex_dict[hex]["sum_clipped_children"], 1)
        #             hex_dict[hex]["clipped"] = min(hex_dict[hex]["dens_lmt"], hex_dict[hex]["sum_clipped_children"])
        #
        #
        # #
        # # # calculate scaling factor for each hex
        # # # this may not be needed anymore
        # # for hex in hex_dict:
        # #     res = h3.h3_get_resolution(hex)
        # #     if (res < 11):
        # #         hex_dict[hex]["scaling"] = min(hex_dict[hex]["dens_lmt"]/hex_dict[hex]["n"], 1)
        # # del hex, res
        #
    # calculate scaling factor per hotspot
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
                            temp_scaling_list.append(hex_dict[res][hex_adr]["unclipped"])
                            first_loop = False
                        else:
                            temp_scaling_list.append(hex_dict[res][hex_adr]["unclipped"])
                except KeyError:
                    continue
        except KeyError: # KeyError because it has no parent hex addresses, just continue
            continue
        temp_list = numpy.prod(temp_scaling_list)
        temp_var = h.hspot_by_addr[hspot]["reward_scale"] #debug
        h.hspot_by_addr[hspot]["scaling_by_hex"] = temp_scaling_list
        h.hspot_by_addr[hspot]["tx_rwd_scaling"] = temp_list
        # #
        # #
        # #
        # #
        # #
        # #
        # # # Testing purposes only
        # # # TSA hex_8 = "882aac8883fffff"
        # # # TSA addr = "11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke"
        # # multiplier = hex_dict["882aac8883fffff"]["good_neighbors"] + 1 - res_vars[8][0] + 1
        # # gn = hex_dict["882aac8883fffff"]["good_neighbors"]
        # # scaling = h.hspot_by_addr["11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke"]["tx_rwd_scaling"] # for TMC
        # # hex_dit_ex = hex_dict["882aac8883fffff"]
        # # print(f"hex dict: {hex_dit_ex}")
        # # print(f"Good neighbors: {gn}")
        # # print(f"max: {res_vars[8][2]}")
        # # print(f"tgt: {res_vars[8][1]}")
        # # print(f"multiplier: {multiplier}")
        # # print(hex_dict["882aac8883fffff"]["dens_lmt"])
        # # print(hex_dict["882aac8883fffff"]["scaling"])
        # # print(f"Transmit Reward Scaling: {scaling}")
        # # print(f"Unasserted: {unasserted}")
        # # del gn, multiplier, unasserted, scaling, hex_dit_ex
        # #
        # # TSA_hex_7 = "872aac888ffffff"
        # # res = 7
        # # # TSA addr = "11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke"
        # # multiplier = hex_dict[TSA_hex_7]["good_neighbors"] + 1 - res_vars[res][0] + 1
        # # gn = hex_dict[TSA_hex_7]["good_neighbors"]
        # # scaling = h.hspot_by_addr["11dZ9ow9HZQj3GJEBdFXxkzVHbBfxKyJJ9P11LvkFvqgm1TYzke"]["tx_rwd_scaling"] # for TMC
        # # print(f"Hex dict: {hex_dict[TSA_hex_7]}")
        # # print(f"Good neighbors: {gn}")
        # # print(f"max: {res_vars[res][2]}")
        # # print(f"tgt: {res_vars[res][1]}")
        # # print(f"multiplier: {multiplier}")
        # # print(hex_dict[TSA_hex_7]["dens_lmt"])
        # # print(hex_dict[TSA_hex_7]["scaling"])
        # # print(f"Transmit Reward Scaling: {scaling}")
        # # del gn, multiplier, scaling, res, TSA_hex_7
        # #
    no_match_1 = 0
    no_match_01 = 0
    no_match_001 = 0
    no_match_0001 = 0
    match = 0
    unasserted_2 = 0
        #
    # Checks calculated scaling vs API scaling
    # Make into fuction and send warning if this number is off when code is complete
    code_tester = {}
    for hspot in h.hspot_by_addr:
        try:
            API = h.hspot_by_addr[hspot]["reward_scale"]  # debug
            my_score = h.hspot_by_addr[hspot]["tx_rwd_scaling"]  # debug
            abs_diff = abs(API - my_score)
            code_tester[hspot] = [abs_diff, my_score, API]

            if abs_diff >= 0.1:
                no_match_1 += 1
            elif abs_diff >= 0.01:
                no_match_01 += 1
            elif abs_diff >= 0.001:
                no_match_001 += 1
            elif abs_diff >= 0.0001:
                no_match_0001 += 1
            else:
                match += 1
                # print(f"{hspot} : {API} : {my_score}") #debug
        except (TypeError, KeyError):
            unasserted_2 += 1
    sorted_tuples = sorted(code_tester.items(), key=lambda item: item[1])
    code_tester = {k: v for k, v in sorted_tuples}
    # print(code_tester)
    # print("Hotspot Address:                                      Absolute difference                my_score             API")
    # print(f"{no_match_1+no_match_01+no_match_001+no_match_0001+match+unasserted_2} {len(h.hspot_by_addr)}")
    if no_match_1+no_match_01+no_match_001+no_match_0001+match+unasserted_2 != len(h.hspot_by_addr):
        print("Not all hotspots accounted for")
    if no_match_1+no_match_01+no_match_001+no_match_0001 > 0:
        print(f"Total no match {no_match_1+no_match_01+no_match_001+no_match_0001}")
        print(f"no match 0.1: {no_match_1}")
        print(f"no match 0.01: {no_match_01}")
        print(f"no match 0.001: {no_match_001}")
        print(f"no match 0.0001: {no_match_0001}")
        print(f"Total no match: {no_match_1+no_match_01+no_match_001+no_match_0001}")
        print(f"Unasserted 2: {unasserted_2}")

    return hex_dict