import falcon
from falcors import CORS
from resources.tournaments import Tournaments
from resources.scores import Scores

cors = CORS(allow_all_origins=True)

api = falcon.API(middleware=[cors.middleware])
api.add_route('/api/tournaments', Tournaments())
api.add_route('/api/tournaments/{tour_id}', Tournaments(), suffix='single')
api.add_route('/api/tournaments/{tour_id}/scores/my', Scores(), suffix='my')
api.add_route('/api/tournaments/{tour_id}/scores/{player_id}', Scores())
