import logging
from .. import constants as const
from ..dispatcher import api
from ..mapping import mapper

LOGGER = logging

class Fetcher:

    def __init__(self, url = const.DISPATCHER_URL):
        self.dispatcher_url = url

    def get_all_tournaments(self):

        tournaments = []

        #get all instance indexes
        dispatcher_api = api.API(url=self.dispatcher_url)
        indexes = dispatcher_api.get_instance_indexes()

        #getting all instances if any
        if indexes:
            tour_mapper = mapper.Mapper()
            for index in indexes:
                dapp = dispatcher_api.get_instance(index)
                tournaments.append(tour_mapper.to_tournament(dapp))

        return tournaments
