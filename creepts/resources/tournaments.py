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
import logging
from datetime import datetime
import pytz
from .. import constants as const
from ..utils import tournament_recovery_utils as tru
from ..model.tournament import TournamentJSONEncoder, TournamentPhase

LOGGER = logging

class Tournaments:
    def on_get(self, req, resp):
        """
        Handles the get method for Tournaments resource

        Parameters
        ----------
        req : falcon.Request
            Contains the request, including query string parameters:
            - limit: int
                Maximum number of tournaments to return (default applies if not specified)
            - offset: int
                Pagination offset, 10 returns 10th element up to (10+limit)th element
            - phase: str -> Enum:"commit" "reveal" "round" "end"
                Filter tournaments by phase
            - me: bool
                Filter tournaments which I am participating
            - sort_by: str -> Enum:"playerCount" "deadline"
                Sort criteria of returned tournaments
            - order_by: str ->  Enum:"asc" "desc"
                Ascendent or descendent order of returned tournaments. Default is asc

        resp: falcon.Response
            This object is used to issue the response to this call it,
            if no error occurs, it should return a structure describing the
            tournaments similar to the one available in:
            <project_root>/reference/anuto/examples/tournaments.json

        Returns
        -------
        NoneType
            This method has no return
        """

        #If a phase filter was provided, checking it has a valid value
        if req.has_param("phase"):
            valid_values = [phase.value for phase in TournamentPhase]
            if (req.params["phase"] not in valid_values):
                raise falcon.HTTPBadRequest(description="Invalid phase filter provided, valid values are {}".format(valid_values))

        try:
            LOGGER.info("Get tournaments")
            #Recoverign all tournaments from dispatcher
            tournaments_fetcher = tru.Fetcher()

            tournaments = tournaments_fetcher.get_all_tournaments()

            #Recovering scores from db and blockchain
            tournaments = tournaments_fetcher.populate_scores_from_db(tournaments)

            filtered_tournaments = []

            #If no filter, return all
            if ((not req.has_param("phase")) and (not req.has_param("me"))):
                filtered_tournaments = tournaments

            else:
                #There is a filter, filtering
                for tour in tournaments:
                    #If there is a phase parameter, exclude the ones not matching
                    if req.has_param("phase"):
                        if (str(tour.phase.value) != req.params["phase"]):
                            continue

                    #if there is a me parameter, exclude the ones not matching
                    if req.has_param("me"):
                        if req.params["me"] == "true":
                            #Exclude if doesn't match
                            if const.PLAYER_OWN_ADD not in tour.scores.keys():
                                continue
                        elif req.params["me"] == "false":
                            #Exclude if matches
                            if const.PLAYER_OWN_ADD in tour.scores.keys():
                                continue

                    filtered_tournaments.append(tour)

            #TODO: sort and order by desc/asc
            #Build response dict with the filtered tournaments
            resp_dict = {}

            offset = 0
            if req.has_param("offset"):
                offset = int(req.params["offset"])

            limit = const.TOURNAMENTS_RESPONSE_LIMIT
            if req.has_param("limit"):
                limit = int(req.params["limit"])

            resp_dict["limit"] = limit
            resp_dict["offset"] = offset
            resp_dict["results"] = filtered_tournaments[offset:offset+limit]

            resp.body = json.dumps(resp_dict, cls=TournamentJSONEncoder)
            resp.status = falcon.HTTP_200

        except Exception as e:
            LOGGER.exception(e)
            raise falcon.HTTPInternalServerError(description="Failed retrieving tournaments")

    def on_get_single(self, req, resp, tour_id):
        """
        Handles the get method for a single Tournament

        Parameters
        ----------
        req : falcon.Request
            Contains the request

        resp: falcon.Response
            This object is used to issue the response to this call it,
            if no error occurs, it should return a structure describing the
            tournament similar to the one available in:
            <project_root>/reference/anuto/examples/tournament.json

        tour_id : str
            The id of the desired tournament

        Returns
        -------
        NoneType
            This method has no return
        """

        try:
            #Recoverign tournament from dispatcher, if it exists
            tournaments_fetcher = tru.Fetcher()

            tour = tournaments_fetcher.get_tournament(tour_id)

            if tour:
                #Found the tournament

                #Recovering scores from db and blockchain
                tour_with_scores = tournaments_fetcher.populate_scores_from_db([tour])[0]

                resp.body = json.dumps(tour_with_scores, cls=TournamentJSONEncoder)
                resp.status = falcon.HTTP_200
                return

        except Exception as e:
            LOGGER.exception(e)
            raise falcon.HTTPInternalServerError(description="Failed retrieving tournament")

        #No matches, return 404
        raise falcon.HTTPNotFound(description="No tournament with the provided id")
