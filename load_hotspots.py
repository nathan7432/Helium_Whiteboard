import json
import urllib.request
import urllib.error
import time

def load_hotspots(force=False):
    try:
        if force:
            raise FileNotFoundError
        with open('hotspots.json', 'r') as fd:
            dat = json.load(fd)
            if time.time() - dat['time'] > 72*3600:
                # print(f"-W- hotspot cache is over 2 days old consider refreshing 'python3 utils.py -x refresh_hotspots'")
                raise FileNotFoundError
            if not dat['hotspots']:
                raise FileNotFoundError
            return dat['hotspots']
    except (FileNotFoundError, json.JSONDecodeError) as e:
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
                #print(resp.get('data'))
                hotspots.extend(resp.get('data'))
                print(f"-I- found {len(hotspots)} hotspots")
                if len(resp.get('data', [])) < 1000 or cursor is None:
                    break

            dat = dict(
                time=int(time.time()),
                hotspots=hotspots
            )
            json.dump(dat, fd, indent=2)
        return hotspots


