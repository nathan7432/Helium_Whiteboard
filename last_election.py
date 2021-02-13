import json
import urllib.request


def consensus_height():
    current_height = json.load(urllib.request.urlopen("https://api.helium.io/v1/blocks/height"))
    current_height = current_height["data"]['height']

    while True:
        retur = json.load(urllib.request.urlopen(f"https://api.helium.io/v1/blocks/{current_height}/transactions"))

        for item in retur["data"]:
            if item["type"] == "consensus_group_v1":
                return current_height
        current_height -= 1


def main():
    print(consensus_height())

main()