import json
import urllib.request
import urllib.error
import time

def load_hotspots(force=False):
    print("Running load_hotspots")
    try:
        if force:
            raise FileNotFoundError
        with open('hotspots.json', 'r') as fd:
            dat = json.load(fd)
            if time.time() - dat['time'] > 72*3600:
                print(f"Over two days old, refreshing")
                raise FileNotFoundError
            if not dat['hotspots']:
                print(f"dat not found, refreshing")
                raise FileNotFoundError
            return [dat['last_cg'], dat['hotspots']]
    # returns last cg and list of hotspots
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # added by n8, finds last cg
        print("Searching blockchain for last consensus group...")
        current_height = json.load(urllib.request.urlopen("https://api.helium.io/v1/blocks/height"))
        current_height = current_height["data"]['height']

        consensus_loop = True
        while consensus_loop:
            retur = json.load(
                urllib.request.urlopen(f"https://api.helium.io/v1/blocks/{current_height}/transactions"))

            for item in retur["data"]:
                if item["type"] == "consensus_group_v1":
                    print("Last cg found!")
                    last_cg = current_height
                    consensus_loop = False
                    break
            current_height -= 1
        # refreshes json, adds time, last cg, and hotspots
        with open('hotspots.json', 'w') as fd:
            cursor = None
            hotspots = []
            while True:
                url = 'https://api.helium.io/v1/hotspots'
                if cursor:
                    url += '?cursor=' + cursor
                resp = json.load(urllib.request.urlopen(url))
                cursor = resp.get('cursor')

                if not resp.get('data'):
                    break
                hotspots.extend(resp.get('data'))
                print(f"-I- found {len(hotspots)} hotspots")
                if len(resp.get('data', [])) < 1000 or cursor is None:
                    break

            dat = dict(
                time=int(time.time()),
                last_cg=last_cg,
                hotspots=hotspots
            )
            json.dump(dat, fd, indent=2)  # what goes in the file, what file, indent

        retur_list = []
        retur_list.append(last_cg)
        retur_list.append(hotspots)
        return retur_list
