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
import traceback
import sys
import requests
import logging

from .. import constants as const
from ..utils import game_log_utils, hash_utils
from ..db import db_utilities

LOGGER = logging.getLogger(__name__)


class Scores:

    def on_put_my(self, req, resp, tour_id):
        """
        Handles the put method for the own score of a given tournment

        Parameters
        ----------
        req : falcon.Request
            Contains the request

        resp: falcon.Response
            This object is used to issue the response to this call,
            if no error occurs, it returns a 204 if there was a score
            and it was improved and a 201 if it is the 1st score stored
            if there is already a log with better score, it returns
            a 409 - Conflict, you already have a better score response
            if the tournament is not accepting logs, it returns
            a 403 - Forbidden, tournament is not accepting gameplays
            if there is no tournament with the provided id, returns 404

        tour_id : str
            The id of the desired tournament

        Returns
        -------

        NoneType
            This method has no return
        """

        #TODO: validate the json payload
        if not req.content_type:
            raise falcon.HTTPBadRequest(description="Provide a valid JSON as payload for this method")
        if 'application/json' not in req.content_type:
            raise falcon.HTTPUnsupportedMediaType(description="The payload must be sent in json format")

        #WARNING! Mocked response
        #Check if the is a tournament with this id
        with open("./reference/anuto/examples/tournaments.json", 'r', encoding="utf8") as sample_tour_file:
            tournaments_json = sample_tour_file.read()
            tournaments_struct = json.loads(tournaments_json)

            if ("results" not in tournaments_struct.keys()):
                raise falcon.HTTPInternalServerError(description="Malformed mocked tournaments file, no results entry")

            #Retrieving the desired tournament
            found = False
            for tour in tournaments_struct["results"]:
                if ("id" not in tour.keys()):
                    raise falcon.HTTPInternalServerError(description="Malformed mocked tournaments file, no id entry in tournament: \n{}".format(json.dumps(tour)))
                if (tour["id"].strip() == tour_id.strip()):
                    #Checking the tournament is in commit phase
                    if (tour['phase'] != 'commit'):
                        #It isn't return 403
                        raise falcon.HTTPForbidden(description="The tournament for the provided id is not in the commit phase: \n{}".format(json.dumps(tour)))
                    #Tournament found and in commit phase
                    found = True
                    break
            if not found:
                #Not found, return 404
                raise falcon.HTTPNotFound(description="No tournament found with the provided id: {}".format(tour_id))

        #Getting request json
        req_json = req.media
        user_id = const.PLAYER_OWN_ADD
        score = req_json['score']
        waves = req_json['waves']
        log_bytes = json.dumps(req_json['log']).encode()

        #Check if there is already a score and log for this tournament in db
        log_entry = db_utilities.select_log_entry(user_id, tour_id)

        if log_entry:
            previous_score = log_entry[2]
            #Check if score is higher than the one stored
            if (score > previous_score):
                #It is, store it
                db_utilities.update_log_entry(user_id, tour_id, score, waves, log_bytes)
                resp.status = falcon.HTTP_204
            else:
                #It isn't return 409
                raise falcon.HTTPConflict(description="The given score is not higher than a previously submitted one")
        else:
            #No previous entry, store
            db_utilities.insert_log_entry(user_id, tour_id, score, waves, log_bytes)
            resp.body = json.dumps({"title":"201 Created","description":"Score, wave number and log were created for tournament {}".format(tour_id)})
            resp.status = falcon.HTTP_201

    def on_get_my(self, req, resp, tour_id):
        """
        Handles the get method for the own score of a given tournment

        Parameters
        ----------
        req : falcon.Request
            Contains the request

        resp: falcon.Response
            This object is used to issue the response to this call,
            if no error occurs, it returns a structure with the score,
            reached wave number and log of actions that earned that score
            and reached that wave number
            if there is no score/log/wave number for the given tornament
            id, returns 404 - Not Found

        tour_id : str
            The id of the desired tournament

        Returns
        -------

        NoneType
            This method has no return
        """

        user_id = const.PLAYER_OWN_ADD

        #Querying database and checking if there is already a score and log
        #for this tournament in db
        log_entry = db_utilities.select_log_entry(user_id, tour_id)
        if log_entry:
            #There is, return it
            resp_payload={}
            resp_payload['score'] = log_entry[2]
            resp_payload['wave'] = log_entry[3]
            resp_payload['log'] = json.loads(log_entry[4].decode('UTF-8'))
            resp.body = json.dumps(resp_payload)
            resp.status = falcon.HTTP_200
            return

        #There isn't, return 404
        raise falcon.HTTPNotFound(description="There is no score/log/wave number for the tornament {}".format(tour_id))

    def on_get(self, req, resp, tour_id, player_id):
        """
        Handles the get method for the score of the given player and tournment

        Parameters
        ----------
        req : falcon.Request
            Contains the request

        resp: falcon.Response
            This object is used to issue the response to this call,
            if no error occurs, it returns a structure with the score,
            reached wave number and log of actions that earned that score
            and reached that wave number
            if there is no score/log/wave number for the given tournament
            id and player id, returns 404 - Not Found

        tour_id : str
            The id of the desired tournament

        player_id : str
            The id of the desired player

        Returns
        -------

        NoneType
            This method has no return
        """

        #Warning! Mocked response
        #Check if the is a tournament with this id
        with open("./reference/anuto/examples/tournaments.json", 'r', encoding="utf8") as sample_tour_file:
            tournaments_json = sample_tour_file.read()
            tournaments_struct = json.loads(tournaments_json)
            resp_payload = {}

            if ("results" not in tournaments_struct.keys()):
                raise falcon.HTTPInternalServerError(description="Malformed mocked tournaments file, no results entry")

            #Retrieving the desired tournament
            found = False
            for tour in tournaments_struct["results"]:
                if ("id" not in tour.keys()):
                    raise falcon.HTTPInternalServerError(description="Malformed mocked tournaments file, no id entry in tournament: \n{}".format(json.dumps(tour)))
                if (tour["id"].strip() == tour_id.strip()):
                    #Checking the tournament has a well-formed score for the given player
                    if ("scores" not in tour.keys()):
                        raise falcon.HTTPNotFound(description="No score found for tournament {} for a player with the provided id: {}".format(tour_id, player_id))
                    if (player_id not in tour["scores"].keys()):
                        raise falcon.HTTPNotFound(description="No score found for tournament {} for a player with the provided id: {}".format(tour_id, player_id))
                    if ('score' not in tour["scores"][player_id].keys()):
                        raise falcon.HTTPInternalServerError(description="Malformed mocked tournaments file, no score set for player {} for tournament {}".format(player_id, tour_id))
                    if ('waves' not in tour["scores"][player_id].keys()):
                        raise falcon.HTTPInternalServerError(description="Malformed mocked tournaments file, no waves set for player {} for tournament {}".format(player_id, tour_id))
                    resp_payload["score"] = tour["scores"][player_id]["score"]
                    resp_payload["waves"] = tour["scores"][player_id]["waves"]
                    resp_payload["log"] = game_log_utils.get_game_log(tour_id, player_id)
                    #Just for the mocked method
                    if not resp_payload["log"]:
                        raise falcon.HTTPNotFound(description="No score found for tournament {} for a player with the provided id: {}".format(tour_id, player_id))
                    resp.body = json.dumps(resp_payload)
                    resp.status = falcon.HTTP_200
                    return

        #Not found, return 404
        raise falcon.HTTPNotFound(description="There is no tournament {}".format(tour_id))


