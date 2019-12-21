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

    def on_put_commit(self, req, resp, tour_id):
        """
        Handles the put method for committing the own score of a given tournment

        Parameters
        ----------
        req : falcon.Request
            Contains the request

        resp: falcon.Response
            This object is used to issue the response to this call,
            if no error occurs, it returns a 204 if there was a score
            and it was committed, 412 if there was no score to commit,
            403 if the tournament is not in the commit phase,
            if there is no tournament with the provided id, returns 404

        tour_id : str
            The id of the desired tournament

        Returns
        -------

        NoneType
            This method has no return
        """

        '''
        #TODO: perform the validations bellow
        #Checking if there is the desired tournament
            #Tournament found, checking it is in the commit phase
                #Not in the commit phase raise exception
                raise falcon.HTTPForbidden(description="The tournament for the provided id is not in the commit phase: \n{}".format(json.dumps(tour)))

            #Tournament not found
            raise falcon.HTTPNotFound(description="No tournament found with the provided id: {}".format(tour_id))
        '''

        #Recover score for the given tournament

        #Check if there is already a score and log for this tournament in db
        user_id = const.PLAYER_OWN_ADD
        log_entry = db_utilities.select_log_entry(user_id, tour_id)

        if log_entry:
            game_log = log_entry[4]

            #Write log to file with the tour_id as name
            log_filename = "{}{}.json".format(LOG_FILES_OUTPUT_DIR, tour_id)

            with open(log_filename, 'w') as log_file:
                log_file.write(game_log)

            #Compress and archive the log
            packed_log_filename = hash_utils.pack_log_file(log_filename)

            if not packed_log_filename:
                raise falcon.HTTPInternalServerError(description="Error compressing and archiving game log file")

            #Truncate file to the expected final size
            success = hash_utils.truncate_file(packed_log_filename)

            if not success:
                raise falcon.HTTPInternalServerError(description="Error truncating compressed and archived game log file to correct size")

            #Calculate the merkle tree root hash of it
            calculated_hash = hash_utils.merkle_root_hash(packed_log_filename)

            if not calculated_hash:
                raise falcon.HTTPInternalServerError(description="Error calculating the merkle root hash of the compressed, archieved and truncated game log file")

            #Format the post payload
            payload = {
                "action": "commit",
                "params": {
                    "hash": calculated_hash
                }
            }
            data = {
                "Post": {
                "index": tour_id,
                "payload": json.dumps(payload)
                }
            }

            #Commit the game log
            dispatcher_resp = requests.post(const.COMMIT_LOG_URL, json=json.dumps(data))

            if (dispatcher_resp.status_code != 200):
                LOGGER.error("Failed to commit gamelog for tournament id {} and game log file name {}. Response content was {}".format(tour_id, packed_log_filename, dispatcher_resp.text))
                raise falcon.HTTPInternalServerError(description="Failed to commit the gamelog for tournament id {} and game log filename {}".format(tour_id, packed_log_filename))

            #Game log correctly commited, set status code to 204 and return
            resp.status = falcon.HTTP_204
            return

        #No score
        raise falcon.HTTPPreconditionFailed(description="There was no saved game log for the desired tournament. Tournament id: {}".format(tour_id))


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


