import json
import pandas as pd
# I have instrument.json in './data' folder. I will load it. from my pairs list ["EUR", "USD", "GBP"] I will check for all cross. If it is there I will append it in a new list that will then be called by get_data function.

def get_all_possible_pairs(pairs):
    possible_pairs = []
    # Load the instrument.json file
    with open('./data/instruments.json', 'r') as file:
        instruments = json.load(file)
    for p1 in pairs:
        for p2 in pairs:
            pair = f"{p1}_{p2}"
            if pair in instruments.keys():
                possible_pairs.append(pair)
    # print(possible_pairs)
    return possible_pairs


def get_data(ins_collection, api, pairs, granularities, count, to_date=None, from_date=None,price="MBA"):
    possible_pairs = get_all_possible_pairs(pairs)
    for pair in possible_pairs:
        for granularity in granularities:
            ins_collection.create_data_file(api, pair_name=pair, granularity=granularity, count=count)