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
from .contract import Contract
from .. import constants as const

class API:

    def __init__(self, url = const.DISPATCHER_URL):
        self.url = url

    def get_instance_indexes(self):
        headers = {'Content-type': 'application/json'}
        response = requests.get(self.url, headers=headers)
        # TODO: handle errors
        if (response.status_code == 200):
            return response.json()
        else:
            return None

    def get_instance(self, index):
        response = requests.get(self.url, json={"Instance": index})
        
        # TODO: handle errors
        json_response = response.json()

        # instantiate a Contract wrapper class with the json
        return Contract(json_response)
