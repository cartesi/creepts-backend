import falcon
import logging
import logging.config
from falcors import CORS
from . import constants as const

#Configuring the logging for the application
logging.config.fileConfig(const.LOGGING_CONFIG_FILENAME)

LOGGER = logging

#Import mocked resources if MOCKED_SERVER is set
if const.MOCKED_SERVER:
    LOGGER.debug("Importing mocked resources")
    from .tests.mock_tournaments import Tournaments
    from .tests.mock_scores import Scores
else:
    LOGGER.debug("Importing real resources")
    from .resources.tournaments import Tournaments
    from .resources.scores import Scores


cors = CORS(
    allow_all_origins=True,
    allow_methods_list=['GET', 'PUT', 'POST'],
    allow_headers_list=['content-type'])

api = falcon.API(middleware=[cors.middleware])
api.add_route('/api/tournaments', Tournaments())
api.add_route('/api/tournaments/{tour_id}', Tournaments(), suffix='single')
api.add_route('/api/tournaments/{tour_id}/scores/my', Scores(), suffix='my')
api.add_route('/api/tournaments/{tour_id}/scores/{player_id}', Scores())
