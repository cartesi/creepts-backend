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
import os

from .. import constants as const
from ..utils import game_log_utils, hash_utils, blockchain_utils
from ..db import db_utilities
from ..logger import LoggerClient
from ..utils import tournament_recovery_utils as tru
from ..model.tournament import TournamentPhase

class Scores:

    def __init__(self, address):
        self.tournaments_fetcher = tru.Fetcher(address)

    def on_put_my(self, req, resp, tournament_id):
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

        tournament_id : str
            The id of the desired tournament

        Returns
        -------

        NoneType
            This method has no return
        """

        error = None
        try:
            logging.info("PUT score")
            #TODO: validate the json payload
            if not req.content_type:
                error = falcon.HTTPBadRequest(description="Provide a valid JSON as payload for this method")
                raise
            if 'application/json' not in req.content_type:
                error = falcon.HTTPUnsupportedMediaType(description="The payload must be sent in json format")
                raise

            #Check if the is a tournament with this id
            tour = self.tournaments_fetcher.get_tournament(tournament_id)

        except Exception as e:
            if error:
                logging.exception(error)
                raise error

            logging.exception(e)
            raise falcon.HTTPInternalServerError(description="Failed recovering tournament")

        if not tour:
            #Not found, return 404
            raise falcon.HTTPNotFound(description="No tournament found with the provided id: {}".format(tournament_id))

        # if server is in read-only mode, respond successfully as if score was submitted
        # this is for testing purposes, in the future we may support a real read-only mode, including the 
        # front-end in the process, with proper user feedback
        if const.READ_ONLY:
            logging.info("Server in read-only mode, returning 201 and not submitting log")
            resp.body = json.dumps({"title":"201 Created","description":"Server in read-only mode"})
            resp.status = falcon.HTTP_201
            return

        #Checking the tournament is in the commit phase
        if tour.phase != TournamentPhase.COMMIT:
            #It isn't return 403
            phase = None
            if tour.phase:
                phase = tour.phase.value
            raise falcon.HTTPForbidden(description="The tournament with id {} is not in the commit phase. Tournament phase: {}".format(tournament_id, phase))

        try:
            #Getting request json
            req_json = req.media
            user_id = const.PLAYER_OWN_ADD
            score = req_json['score']
            waves = req_json['waves']
            log_bytes = json.dumps(req_json['log']).encode()

            #Check if there is already a score and log for this tournament in db
            log_entry = db_utilities.select_log_entry(user_id, tournament_id)

            if log_entry:
                previous_score = log_entry[2]
                #Check if score is higher than the one stored
                if (score > previous_score):
                    #It is, store it
                    db_utilities.update_log_entry(user_id, tournament_id, score, waves, log_bytes)
                    #Commit the log
                    error = self._commit_log(tournament_id, log_bytes)
                    if error:
                        raise
                    resp.status = falcon.HTTP_204
                else:
                    #It isn't return 409
                    error = falcon.HTTPConflict(description="The given score is not higher than a previously submitted one")
                    raise
            else:
                #No previous entry, store
                db_utilities.insert_log_entry(user_id, tournament_id, score, waves, log_bytes)
                #Commit the log
                error = self._commit_log(tournament_id, log_bytes)
                if error:
                    raise
                resp.body = json.dumps({"title":"201 Created","description":"Score, wave number and log were created for tournament {}".format(tournament_id)})
                resp.status = falcon.HTTP_201

        except Exception as e:
            if error:
                logging.exception(error)
                raise error

            logging.exception(e)
            raise falcon.HTTPInternalServerError(description="Failed saving and committing game log")


    def on_get_my(self, req, resp, tournament_id):
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

        tournament_id : str
            The id of the desired tournament

        Returns
        -------

        NoneType
            This method has no return
        """

        user_id = const.PLAYER_OWN_ADD

        #Querying database and checking if there is already a score and log
        #for this tournament in db
        log_entry = db_utilities.select_log_entry(user_id, tournament_id)
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
        raise falcon.HTTPNotFound(description="There is no score/log/wave number for the tornament {}".format(tournament_id))

    def on_get(self, req, resp, tournament_id, player_id):
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

        tournament_id : str
            The id of the desired tournament

        player_id : str
            The address of the desired player

        Returns
        -------

        NoneType
            This method has no return
        """

        error = None
        try:
            #Check if provided player_id is a valid eth address
            if not blockchain_utils.is_address(player_id):
                raise falcon.HTTPBadRequest(description="Provided player address is not a valid Ethereum address: {}".format(player_id))

            #Check if there is a tournament with this id
            tour = self.tournaments_fetcher.get_tournament(tournament_id)

            if not tour:
                #Not found, return 404
                raise falcon.HTTPNotFound(description="No tournament found with the provided id: {}".format(tournament_id))

            #Making sure the tournament is not in the commit phase
            if tour.phase == TournamentPhase.COMMIT:
                #It isn't return 400
                raise falcon.HTTPBadRequest(description="The tournament with id {} is still in the commit phase".format(tournament_id))

            # get score from tour.scores, which already contains scores from self, opponent and winner (if they exist)

            #Making sure the player is participating in the given tournament
            if player_id not in tour.scores:
                #It doesn't return 400
                raise falcon.HTTPBadRequest(description="Player {} is not myself, or my opponent or the winner in tournament {}".format(player_id, tournament_id))

            # commit hash
            commit_hash = tour.scores[player_id]['hash']

            # download file (or initiates a download)
            logger_client = LoggerClient()
            response = logger_client.download(commit_hash)

            if response['status'] == 0:
                # 0 -> finished successfully
                resp_dict = {}
                resp_dict['score'] = tour.scores[player_id]['score']

                # load json into object
                log_filename = hash_utils.unpack_log_file(response['path'])
                if log_filename is None:
                    raise falcon.HTTPInternalServerError(description="Could not unpack file")

                # load json object from file
                with open(log_filename) as json_file:
                    log = json.load(json_file)

                resp_dict['log'] = log
                resp.body = json.dumps(resp_dict)
                resp.status = falcon.HTTP_200
                
            elif response['status'] == 1:
                # 1 -> working on it, not ready yet
                resp.body = json.dumps({ 'progress': response['progress'] })
                resp.status = falcon.HTTP_202

        except Exception as e:
            logging.exception(e)
            if isinstance(e, falcon.HTTPError):
                raise e
            elif isinstance(e, ValueError):
                raise falcon.HTTPBadRequest(description=str(e))
            else:
                raise falcon.HTTPInternalServerError(description=str(e))

    def _commit_log(self, tournament_id, game_log):
        #Write log to file with the tournament_id as name
        log_filename = "{}{}.json".format(const.LOG_FILES_OUTPUT_DIR, tournament_id)
        logging.info("Writting log with filename %s", log_filename)

        with open(log_filename, 'wb') as log_file:
            log_file.write(game_log)

        #Compress and archive the log
        packed_log_filename = hash_utils.pack_log_file(log_filename)

        if not packed_log_filename:
            logging.error("Failed to pack the log file")
            return falcon.HTTPInternalServerError(description="Error compressing and archiving game log file")

        logging.info("Packed log filename is %s", packed_log_filename)

        #Truncate file to the expected final size
        success = hash_utils.truncate_file(packed_log_filename)

        if not success:
            logging.error("Failed to truncate log file")
            return falcon.HTTPInternalServerError(description="Error truncating compressed and archived game log file to correct size")

        #Calculate the merkle tree root hash of it
        calculated_hash = hash_utils.merkle_root_hash(packed_log_filename)

        if not calculated_hash:
            logging.error("Failed to calculate the hash of the provided file")
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
            "index": int(tournament_id),
            "payload": json.dumps(payload)
            }
        }

        #Commit the game log
        logging.debug("Committing log to the dispatcher")
        dispatcher_resp = requests.post(const.COMMIT_LOG_URL, json=data)

        if (dispatcher_resp.status_code != 200):
            logging.error("Failed to commit gamelog for tournament id {} and game log file name {}. Response content was {}".format(tournament_id, packed_log_filename, dispatcher_resp.text))
            return falcon.HTTPInternalServerError(description="Failed to commit the gamelog for tournament id {} and game log filename {}".format(tournament_id, packed_log_filename))

