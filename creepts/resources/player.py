import falcon
import json
import logging
from .. import constants as const

LOGGER = logging

class Player:
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

        try:
            LOGGER.info("Get player")
            resp.body = json.dumps({"address":const.PLAYER_OWN_ADD})
            resp.status = falcon.HTTP_200

        except Exception as e:
            LOGGER.exception(e)
            raise falcon.HTTPInternalServerError(description="Failed retrieving player info")

