import requests
import time
import json

SLEEP_TIME=0.1
DISPATCHER_URL = "http://localhost:3001"
BASE_FILENAME = "instance_step_{}.json"

last_resp = None
index = 0

while True:
    time.sleep(SLEEP_TIME)
    try:
        response = requests.get(DISPATCHER_URL, json={"Instance": 0})
    except Exception as e:
        print(e)
        continue

    if response.status_code != 200:
        print("Not 200 status code")
        continue

    if response.text != last_resp:
        with open(BASE_FILENAME.format(index),'w') as out_file:
            out_file.write(json.dumps(response.json(), indent=4, sort_keys=True))
            index += 1
            print("Saved new dump, index is now {}".format(index))
            last_resp = response.text
