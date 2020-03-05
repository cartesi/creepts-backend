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
import logging
import logging.config
from falcors import CORS
from . import constants as const

#Configuring the logging for the application
logging.config.fileConfig(const.LOGGING_CONFIG_FILENAME)

#Import mocked resources if MOCKED_SERVER is set
if const.MOCKED_SERVER:
    logging.debug("Importing mocked resources")
    from .tests.mock_tournaments import Tournaments
    from .tests.mock_scores import Scores
else:
    logging.debug("Importing real resources")
    from .resources.tournaments import Tournaments
    from .resources.scores import Scores
from .resources.player import Player

cors = CORS(
    allow_all_origins=True,
    allow_methods_list=['GET', 'PUT', 'POST'],
    allow_headers_list=['content-type'])

api = falcon.API(middleware=[cors.middleware])
api.add_route('/api/tournaments', Tournaments())
api.add_route('/api/tournaments/{tournament_id}', Tournaments(), suffix='single')
api.add_route('/api/tournaments/{tournament_id}/scores/my', Scores(), suffix='my')
api.add_route('/api/tournaments/{tournament_id}/scores/{player_id}', Scores())
api.add_route('/api/me', Player())
