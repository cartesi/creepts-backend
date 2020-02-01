"""
Copyright 2020 Cartesi Pte. Ltd.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import requests
import time
import json

QUERY_INDEX = 0
SLEEP_TIME = 0.1
DISPATCHER_URL = "http://localhost:3001"
BASE_FILENAME = "instance_step_{}.json"

last_resp = None
step_index = 0

def get_instance_indexes():
    headers = {'Content-type': 'application/json'}
    response = requests.get(DISPATCHER_URL, headers=headers)
    if (response.status_code == 200):
        return response.json()
    else:
        return None

while True:
    time.sleep(SLEEP_TIME)
    try:
        instances_resp = get_instance_indexes()
        if instances_resp:
            if QUERY_INDEX in [int(idx) for idx in instances_resp]:
                response = requests.get(DISPATCHER_URL, json={"Instance": QUERY_INDEX})
            else:
                print("{} - Index {} not in active instances list".format(time.ctime(), QUERY_INDEX))
                continue
        else:
            print("{} - Index {} not in active instances list".format(time.ctime(), QUERY_INDEX))
            continue

    except Exception as e:
        print("{} - {}".format(time.ctime(), e))
        continue

    if response.status_code != 200:
        print("{} - Not 200 status code".format(time.ctime()))
        continue

    if response.text != last_resp:
        with open(BASE_FILENAME.format(step_index),'w') as out_file:
            out_file.write(json.dumps(response.json(), indent=4, sort_keys=True))
            step_index += 1
            print("{} - Saved new dump, step index is now {}".format(time.ctime(), step_index))
            last_resp = response.text
