import logging
import json
from .. import constants as const
from ..dispatcher import api
from ..mapping import mapper
from ..db import db_utilities as db_utils

LOGGER = logging

class Fetcher:

    def __init__(self, url = const.DISPATCHER_URL):
        self.dispatcher_url = url
        LOGGER.debug("Instantiated fetcher with url %s", const.DISPATCHER_URL)

    def get_all_tournaments(self):

        tournaments = []

        #get all instance indexes
        dispatcher_api = api.API(url=self.dispatcher_url)
        indexes = dispatcher_api.get_instance_indexes()
        LOGGER.debug("Indexes recovered: %s", indexes)

        #getting all instances if any
        if indexes:
            tour_mapper = mapper.Mapper()
            for index in indexes:
                LOGGER.debug("Recovering tournament index %d", index)
                dapp = dispatcher_api.get_instance(index)
                tour = tour_mapper.to_tournament(dapp)
                if tour:
                    LOGGER.debug("Adding to tournaments list")
                    tournaments.append(tour)

        LOGGER.info("Recovered tournaments")
        return tournaments

    def get_tournament(self, tour_id):

        #Get all instance indexes
        dispatcher_api = api.API(url=self.dispatcher_url)
        indexes = dispatcher_api.get_instance_indexes()

        #Checking if there are tournaments
        if indexes:
            int_tour_id = int(tour_id)
            #Checking if given id is among existing tournaments
            if int_tour_id in indexes:
                #Recovering tournament and returning it
                dapp = dispatcher_api.get_instance(int_tour_id)
                LOGGER.info("Returning tournament %s", tour_id)
                tour_mapper = mapper.Mapper()
                return tour_mapper.to_tournament(dapp)

        #Not found
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
                tour.scores=scores_dict[tour.id]

        LOGGER.info("Recovered scores in db for tournaments with ids %s", tournament_ids)
        return tournaments
