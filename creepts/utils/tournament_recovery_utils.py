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

import logging
import json
from .. import constants as const
from ..dispatcher import api
from ..mapping import mapper
from ..mapping import blockchain
from ..db import db_utilities as db_utils

LOGGER = logging

class Fetcher:

    def __init__(self, address, url = const.DISPATCHER_URL):
        self.dispatcher_api = api.API(url)
        self.mapper = mapper.Mapper(address)
        self.blockchainDecorator = blockchain.BlockchainDecorator()
        LOGGER.debug("Instantiated fetcher with url %s", url)

    def get_all_tournaments(self):

        tournaments = []

        # get all instance indexes
        indexes = self.dispatcher_api.get_instance_indexes()
        LOGGER.debug("Indexes recovered: %s", indexes)

        # getting all instances if any
        if indexes:
            for index in indexes:
                LOGGER.debug("Recovering tournament index %d", index)

                # recovering dapp from the dispatcher
                dapp = self.dispatcher_api.get_instance(index)

                # creating a tournament from the dapp
                tournament = self.mapper.to_tournament(dapp)

                if tournament:
                    # complement with information from the blockchain
                    self.blockchainDecorator.apply(dapp, tournament)

                    LOGGER.debug("Adding to tournaments list")
                    tournaments.append(tournament)

        LOGGER.info("Recovered tournaments")
        return tournaments

    def get_tournament(self, tour_id):

        # get all instance indexes
        indexes = self.dispatcher_api.get_instance_indexes()

        # checking if there are tournaments
        if indexes:
            int_tour_id = int(tour_id)
            # checking if given id is among existing tournaments
            if int_tour_id in indexes:
                # recovering dapp from the dispatcher
                dapp = self.dispatcher_api.get_instance(int_tour_id)
                LOGGER.info("Returning tournament %s", tour_id)

                # creating a tournament from the dapp
                tournament = self.mapper.to_tournament(dapp)

                # complement with information from the blockchain
                self.blockchainDecorator.apply(dapp, tournament)

                return tournament

        # not found
        LOGGER.info("Tournament %s not found", tour_id)
        return None

    def populate_scores_from_db(self,tournaments):

        #Getting tournament ids
        tournament_ids = [t.id for t in tournaments]

        #Fetching scores from database
        score_records = db_utils.select_log_entries_from_tournaments(tournament_ids)

        #Organizing score records in a formatted dictionary
        scores_dict={}

        for score_record in score_records:
            user_id = score_record[0]
            tour_id = int(score_record[1])
            score_val = score_record[2]
            wave = score_record[3]

            if tour_id not in scores_dict.keys():
                scores_dict[tour_id] = {}

            scores_dict[tour_id][user_id]={"score":score_val, "waves":wave}

        #Putting the right scores in each tournament object
        for tour in tournaments:
            if tour.id in scores_dict.keys():
                #Merge newly recovered scores with eventual ones that existed before
                tour.scores={**tour.scores, **scores_dict[tour.id]}

        LOGGER.info("Recovered scores in db for tournaments with ids %s", tournament_ids)
        return tournaments
