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

import falcon
import json
import logging
from web3 import Web3
from ..utils import blockchain_utils

LOGGER = logging

class Player:
    def __init__(self, address):
        if not Web3.isAddress(address) or not Web3.isChecksumAddress(address):
            raise ValueError("'{}' is not a valid eth checksummed account address".format(address))

        # store address
        self.address = address

    def on_get(self, req, resp):
        """
        Handles the get method for Player resource

        Parameters
        ----------
        req : falcon.Request
            Contains the request, this method has no input parameters

        resp: falcon.Response
            This object is used to issue the response to this call it,
            if no error occurs, it should return a json structure describing the
            player information. Currently it consist of the player address

        Returns
        -------
        NoneType
            This method has no return
        """

        LOGGER.info("Get player")
        balance = 0

        try:
            balance = blockchain_utils.get_player_balance(self.address)
        except Exception as e:
            # let's just log the exception and return a zero balance, so it works without the blockchain
            LOGGER.exception(e)

        resp.body = json.dumps({ "address": self.address, "balance": balance })
        resp.status = falcon.HTTP_200
