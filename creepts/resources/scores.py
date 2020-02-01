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
from ..utils import game_log_utils, hash_utils, blockchain_utils
from ..db import db_utilities
from ..utils import tournament_recovery_utils as tru
from ..model.tournament import TournamentPhase

LOGGER = logging

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

        error = None
        try:
            LOGGER.info("PUT score")
            #TODO: validate the json payload
            if not req.content_type:
                error = falcon.HTTPBadRequest(description="Provide a valid JSON as payload for this method")
                raise
            if 'application/json' not in req.content_type:
                error = falcon.HTTPUnsupportedMediaType(description="The payload must be sent in json format")
                raise

            #Check if the is a tournament with this id
            tournaments_fetcher = tru.Fetcher()

            tour = tournaments_fetcher.get_tournament(tour_id)

        except Exception as e:
            if error:
                LOGGER.exception(error)
                raise error

            LOGGER.exception(e)
            raise falcon.HTTPInternalServerError(description="Failed recovering tournament")

        if not tour:
            #Not found, return 404
            raise falcon.HTTPNotFound(description="No tournament found with the provided id: {}".format(tour_id))

        #Checking the tournament is in the commit phase
        if tour.phase != TournamentPhase.COMMIT:
            #It isn't return 403
            phase = None
            if tour.phase:
                phase = tour.phase.value
            raise falcon.HTTPForbidden(description="The tournament with id {} is not in the commit phase. Tournament phase: {}".format(tour_id, phase))

        try:
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
                    #Commit the log
                    error = self._commit_log(tour_id, log_bytes)
                    if error:
                        raise
                    resp.status = falcon.HTTP_204
                else:
                    #It isn't return 409
                    error = falcon.HTTPConflict(description="The given score is not higher than a previously submitted one")
                    raise
            else:
                #No previous entry, store
                db_utilities.insert_log_entry(user_id, tour_id, score, waves, log_bytes)
                #Commit the log
                error = self._commit_log(tour_id, log_bytes)
                if error:
                    raise
                resp.body = json.dumps({"title":"201 Created","description":"Score, wave number and log were created for tournament {}".format(tour_id)})
                resp.status = falcon.HTTP_201

        except Exception as e:
            if error:
                LOGGER.exception(error)
                raise error

            LOGGER.exception(e)
            raise falcon.HTTPInternalServerError(description="Failed saving and committing game log")


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

        error = None
        try:
            #Check if provided player_id is a valid eth address
            if not blockchain_utils.is_address(player_id):
                error = falcon.HTTPBadRequest(description="Provided player address is not a valid Ethereum address: {}".format(player_id))
                raise

            #Check if there is a tournament with this id
            tournaments_fetcher = tru.Fetcher()

            tour = tournaments_fetcher.get_tournament(tour_id)

            if not tour:
                #Not found, return 404
                error = falcon.HTTPNotFound(description="No tournament found with the provided id: {}".format(tour_id))
                raise

            #Making sure the tournament is not in the commit phase
            if tour.phase == TournamentPhase.COMMIT:
                #It isn't return 400
                error = falcon.HTTPBadRequest(description="The tournament with id {} is still in the commit phase".format(tour_id))
                raise

            #Making sure the player is participating in the given tournament
            if not blockchain_utils.player_exists(tour.id, player_id):
                #It doesn't return 400
                error = falcon.HTTPBadRequest(description="There is no player {} enrolled in tournament {}".format(player_id, tour_id))
                raise

            resp_dict = {}
            #Recovering score from player
            resp_dict['score'] = blockchain_utils.get_player_score(tour.id, player_id)

            resp.body = json.dumps(resp_dict)
            resp.status = falcon.HTTP_200

        except Exception as e:
            if error:
                LOGGER.exception(error)
                raise error

            LOGGER.exception(e)
            raise falcon.HTTPInternalServerError(description="Failed recovering score")

    def _commit_log(self, tour_id, game_log):
        #Write log to file with the tour_id as name
        log_filename = "{}{}.json".format(const.LOG_FILES_OUTPUT_DIR, tour_id)
        LOGGER.info("Writting log with filename %s", log_filename)

        with open(log_filename, 'wb') as log_file:
            log_file.write(game_log)

        #Compress and archive the log
        packed_log_filename = hash_utils.pack_log_file(log_filename)

        if not packed_log_filename:
            LOGGER.error("Failed to pack the log file")
            return falcon.HTTPInternalServerError(description="Error compressing and archiving game log file")

        LOGGER.info("Packed log filename is %s", packed_log_filename)

        #Truncate file to the expected final size
        success = hash_utils.truncate_file(packed_log_filename)

        if not success:
            LOGGER.error("Failed to truncate log file")
            return falcon.HTTPInternalServerError(description="Error truncating compressed and archived game log file to correct size")

        #Calculate the merkle tree root hash of it
        calculated_hash = hash_utils.merkle_root_hash(packed_log_filename)

        if not calculated_hash:
            LOGGER.error("Failed to calculate the hash of the provided file")
            return falcon.HTTPInternalServerError(description="Error calculating the merkle root hash of the compressed, archieved and truncated game log file")

        #Format the post payload
        payload = {
            "action": "commit",
            "params": {
                "hash": calculated_hash
            }
        }
        data = {
            "Post": {
            "index": int(tour_id),
            "payload": json.dumps(payload)
            }
        }

        #Commit the game log
        LOGGER.debug("Committing log to the dispatcher")
        dispatcher_resp = requests.post(const.COMMIT_LOG_URL, json=data)

        if (dispatcher_resp.status_code != 200):
            LOGGER.error("Failed to commit gamelog for tournament id {} and game log file name {}. Response content was {}".format(tour_id, packed_log_filename, dispatcher_resp.text))
            return falcon.HTTPInternalServerError(description="Failed to commit the gamelog for tournament id {} and game log filename {}".format(tour_id, packed_log_filename))

