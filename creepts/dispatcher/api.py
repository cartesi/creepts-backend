import requests
from .contract import Contract

class API:

    def __init__(self, url = "http://dispatcher:3001"):
        self.url = url

    # TODO: Indices

    def get_instance(self, index):
        response = requests.get(self.url, json={"Instance": index})
        # TODO: handle errors
        json_response = response.json()
        return Contract(json_response)
