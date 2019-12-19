import requests
from .contract import Contract
from .. import constants as const

class API:

    def __init__(self, url = const.DISPATCHER_URL):
        self.url = url

    def get_instance_indexes(self):
        response = requests.get(self.url)
        if (response.status_code == 200):
            return response.json()
        else:
            return None

    def get_instance(self, index):
        response = requests.get(self.url, json={"Instance": index})
        # TODO: handle errors
        json_response = response.json()
        return Contract(json_response)
